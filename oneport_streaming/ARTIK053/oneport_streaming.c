/****************************************************************************
 *
 * Copyright 2016 Samsung Electronics All Rights Reserved.
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 * http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing,
 * software distributed under the License is distributed on an
 * "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND,
 * either express or implied. See the License for the specific
 * language governing permissions and limitations under the License.
 *
 ****************************************************************************/
/****************************************************************************
 * examples/hello/hello_main.c
 *
 *   Copyright (C) 2008, 2011-2012 Gregory Nutt. All rights reserved.
 *   Author: Gregory Nutt <gnutt@nuttx.org>
 *
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions
 * are met:
 *
 * 1. Redistributions of source code must retain the above copyright
 *    notice, this list of conditions and the following disclaimer.
 * 2. Redistributions in binary form must reproduce the above copyright
 *    notice, this list of conditions and the following disclaimer in
 *    the documentation and/or other materials provided with the
 *    distribution.
 * 3. Neither the name NuttX nor the names of its contributors may be
 *    used to endorse or promote products derived from this software
 *    without specific prior written permission.
 *
 * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
 * "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
 * LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
 * FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
 * COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
 * INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
 * BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS
 * OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED
 * AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
 * LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
 * ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
 * POSSIBILITY OF SUCH DAMAGE.
 *
 ****************************************************************************/

/****************************************************************************
 * Included Files
 ****************************************************************************/

#include <tinyara/config.h>
#include <stdio.h>
#include <tinyara/pwm.h>
#include <fcntl.h>
#include <media/media_recorder.h>
#include <media/media_player.h>
#include <media/media_utils.h>
#include <pthread.h>
#include <unistd.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <apps/shell/tash.h>
#include <sys/select.h>


// wifi value ----------------------------------
const char CMD_WIFI[]="wifi";
const char ARG_START[]="startsta";
const char ARG_JOIN[]="join";

const char ARG_DEFALUTAP[]="soo_2.4G";
const char ARG_DEFALUTPWD[]="75657565";

const char CMD_IF[]="ifconfig";
const char ARG_WL1[]="wl1";
const char ARG_DHCP[]="dhcp";
// ---------------------------------------------

// speaker value -------------------------------
uint8_t Buff1[1024*8];
uint8_t Buff2[1024*8];

struct _WavHeader{
	uint32_t ChunkID;			//4
	uint32_t ChunkSize;			//4
	uint32_t Format;				//4
	uint32_t fmt;					//4
	uint32_t molla;				//4
	uint16_t AudioFormat;		//2
	uint16_t Channel;			//2
	uint32_t SampleRate;		//4
	uint32_t ByteRate;			//4
	uint16_t Block_Align;		//2
	uint16_t BitPerSample;		//2
	uint32_t molla2;
	uint32_t molla3;
}WavHeader;

pthread_t SockDownloadThread;
uint32_t DownSize=0,AllSize=0;
uint8_t *ptr_Play,*ptr_Down;

void *thread_TCP(void* argv);
uint16_t PCM_Recv(int sock,void* buff,uint16_t len);
void PCM_Play(struct pcm* pcm,void* buff,uint16_t len);
int speaker(void);

#define PLAYER_PCM
//----------------------------------------------


// recoder value -------------------------------
int recoder(void);
void* thread_record(void *arg); //record&write thread
int PCM_record(char *buffer); //record function
static bool sock_write(void *ptr, size_t size); //tcp write function

pthread_t  SockWrite;
int write_size= 0; //write 할 PCM byte


//----------------------------------------------

// common value --------------------------------
int sock; //socker number
static int pwmfd = -1;

static void codec_start(void); //Master clock generate
static void codec_stop(void); //Master clock stop

struct pcm *ppc; //PCM number
struct pcm_config config; //PCM configuration

/****************************************************************************
 * hello_main
 ****************************************************************************/

#ifdef CONFIG_BUILD_KERNEL
int main(int argc, FAR char *argv[])
#else
int oneport_streaming_main(int argc, char *argv[])
#endif
{

	bool isSuccess;
	struct sockaddr_in serv_addr;

	// connect wifi
	const char* cmd[4]={CMD_WIFI,ARG_START};

	tash_execute_cmd(cmd,2);
	cmd[1]=ARG_JOIN;
	cmd[2]=ARG_DEFALUTAP;
	cmd[3]=ARG_DEFALUTPWD;
	tash_execute_cmd(cmd,4);

	cmd[0]=CMD_IF;
	cmd[1]=ARG_WL1;
	cmd[2]=ARG_DHCP;
	tash_execute_cmd(cmd,3);

	//socket connection
	sock = socket(PF_INET,SOCK_STREAM,0);
	if(sock==-1){
		printf("sock error\n");return 0;
	}
	memset(&serv_addr,0,sizeof(serv_addr));
	serv_addr.sin_family=AF_INET;
	// serv_addr.sin_addr.s_addr=inet_addr(argv[1]);
	serv_addr.sin_addr.s_addr=inet_addr("192.168.0.134");
	serv_addr.sin_port = htons(5555);

	if (connect(sock, (struct sockaddr *)&serv_addr, sizeof(struct sockaddr_in)) < 0){
		printf("connect error\n");return 0;
	}

	printf("connection complete\n");

	isSuccess = recoder();
	printf("1 isSuccess %s\n", isSuccess);
	if (isSuccess){
		printf("is Success recoder end\n");
	}
	printf("recoder end\n");

	isSuccess = speaker();
	printf("2 isSuccess %s\n", isSuccess);
	if (isSuccess){
		printf("is Success speaker end\n");
	}
	printf("speaker end");

	// if (isSuccess){
	// 	close(sock);
	// }

	return 0;

}

int recoder()
{
	//pcm configuration(channels, rate, format etc)
	config.channels=2;
	config.rate=16000;
	config.format = PCM_FORMAT_S16_LE;
	config.period_size = 4096;
	config.period_count = 4;

	//pcm open, 한 패킷당 size
	ppc= pcm_open(0, 0, PCM_IN, &config);
	write_size = pcm_frames_to_bytes(ppc, pcm_get_buffer_size(ppc));

	//Master clock start
	codec_start();

	//record thread 동작
	pthread_create(&SockWrite, NULL, thread_record, NULL);
	sleep(1);
	printf("Recording... Wait 3 seconds\n");
	//up_mdelay(5000);
	sleep(3);

	/*while(1){
	}*/
	printf("Recording end\n");

	pcm_close(ppc); //pcm close
	codec_stop();// Master clock stop
	// close(sock);
	return true;
}

int speaker()
{
	printf("here in speaker\n");
	DownSize=0;
	//������û��Ŷ����
	write(sock,"had",3);fsync(sock);
	//������Ŷ(44����Ʈ)����
	int size = PCM_Recv(sock,(void*)&WavHeader,44);
	//�ٿ����� ������ 44����Ʈ ����
	DownSize += size;

	//PCM ���� �� Open

	config.channels = WavHeader.Channel;
	config.rate = WavHeader.SampleRate;
	config.format = PCM_FORMAT_S16_LE;
	config.period_size = CONFIG_AUDIO_BUFSIZE;
	config.period_count = CONFIG_AUDIO_NUM_BUFFERS;

	printf("config set complete\n strat pcm_open\n");

	ppc = pcm_open(0, 0, PCM_OUT, &config);
	printf("%d\n",pcm_frames_to_bytes(ppc, pcm_get_buffer_size(ppc)));
	codec_start();

	//Wav���� ũ�� ���� = ������ ������ ����+8
	AllSize = WavHeader.ChunkSize + 8;//Wav File Size caculate

	//����Ŷ����.
	pthread_create(&SockDownloadThread,NULL,thread_TCP,Buff1);
	ptr_Down=Buff2;ptr_Play=Buff1;

	printf("PCM_play\n");
	PCM_Play(ppc ,Buff2, sizeof(Buff1));
	pcm_set_playback_volume(ppc,16);
	while(AllSize-DownSize >= sizeof(Buff1)){
		if(ptr_Down==Buff1){
			ptr_Play=Buff1;
			ptr_Down=Buff2;
		}else{
			ptr_Play=Buff2;
			ptr_Down=Buff1;
		}
		pthread_join(SockDownloadThread,NULL);//����Ŷ �ٹ��������� ����
		pthread_create(&SockDownloadThread,NULL,thread_TCP,ptr_Down);//��Ŷ����
		PCM_Play(ppc ,ptr_Play, sizeof(Buff1));


	}
	pthread_join(SockDownloadThread,NULL);//����Ŷ �ٹ��������� ����

	printf("Now Play Last Packet! size=%d\n",AllSize-DownSize);
	//������ ��û
	write(sock,"ack",3);fsync(sock);
	//���������� ����
	size=PCM_Recv(sock,ptr_Down,AllSize-DownSize);
	PCM_Play(ppc ,ptr_Down, sizeof(Buff1));
	//�ٿ����� ������ ������ �� �ܼ�����
	DownSize+=size;
	printf("*%d,%d\n",DownSize,size);

	//�����Ϸ��Ǿ����� �ֿܼ� ����
	printf("Play Complete!!\n PlaySize=%d \n PullSize=%d\n",DownSize,AllSize);
	//������ �����Ϸ��ɶ����� ����
	pcm_wait(ppc,1);
	//PCM Close
	pcm_close(ppc);
	//���������� ���������� �޾����� ������ �˸�
	write(sock,"end",3);fsync(sock);
	//����Ŭ����
	close(sock);
	codec_stop();

	return true;
}

// speaker function *******************************************************************
void *thread_TCP(void* argv){
	//������ ���ۿ�û
	write(sock,"ack",3);fsync(sock);
	printf("send ack\n");
	//����ũ�⸸ŭ ������ ����(���� 8192)
	int size=PCM_Recv(sock,argv,sizeof(Buff1));
	//�ٿ����� ������ ������
	DownSize+=size;
	//�ܼ�����
	printf("*PlaySize = %d, Play  = %d /100 \n",DownSize,100*DownSize/AllSize);

	return 0;
}

uint16_t PCM_Recv(int soc,void* buff,uint16_t len){

	int sizze,readlen=0;
	sizze=0;
	while(sizze<len){
		readlen=read(soc, buff + sizze, len-sizze);
		sizze+=readlen;
	};
	return sizze;
}

void PCM_Play(struct pcm* pcm,void* buff,uint16_t len){
	int remain,ret;

	remain = pcm_bytes_to_frames(pcm, len);
	while (remain > 0) {
		ret = pcm_writei(pcm, buff + len - pcm_frames_to_bytes(pcm, remain), remain);
		if (ret > 0) {
			remain -= ret;
		}
	}
}
//*************************************************************************************

// recoder function *******************************************************************
void* thread_record(void *arg)
{
	printf("in tread_record\n");
	int ret;
	char *buffer= NULL;
	buffer= (char *)malloc(write_size); //전송할 data buffer size 할당

	printf("strat PCM_record\n");
	while(1){
		ret= PCM_record(buffer); //녹음 시작
	}

	free(buffer);
}

int PCM_record(char *buffer)
{
	int frames;
	int size= 0;

	frames = pcm_readi(ppc, buffer, pcm_bytes_to_frames(ppc, write_size));//PCM recorde data read
	if(frames > 0) {
		size = pcm_frames_to_bytes(ppc, frames);
		sock_write(buffer, size);//PCM data send
		printf("send message size %d\n", size);
	}

	return frames;
}

static bool sock_write(void *ptr, size_t size)
{
	int ret;
	size_t written= 0;

	while (written < size) {
		ret = write(sock, (char *)ptr + written, size - written);
		if (ret < 0) {
			return false;
		}
		written += ret;
	}
	return true;
}
//*************************************************************************************

// common fucntion **********************************************************************
static void codec_start(void)
{
	struct pwm_info_s pwm_info;

	pwmfd = open("/dev/pwm5", O_RDWR);

	if (pwmfd > 0) {
		pwm_info.frequency = 6500000;
		pwm_info.duty = 50 * 65536 / 100;
		ioctl(pwmfd, PWMIOC_SETCHARACTERISTICS, (unsigned long)((uintptr_t)&pwm_info));
		ioctl(pwmfd, PWMIOC_START);
	}
}

static void codec_stop(void)
{
	if (pwmfd > 0) {
		ioctl(pwmfd, PWMIOC_STOP);
		close(pwmfd);
	}
}
//*************************************************************************************
