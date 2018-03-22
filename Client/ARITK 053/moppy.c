#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>

#include <stdio.h>
#include <stdlib.h>

#include <string.h>
#include <sys/socket.h>
#include <errno.h>

#include <tinyara/pwm.h>
#include <apps/graphics/gui.h>

#include <media/media_recorder.h>
#include <media/media_utils.h>
#include <media/media_player.h>

#include <time.h>

//#define HOST "112.221.113.29"
#define HOST "192.168.0.10"
#define PORT 7001
#define BUFF_SIZE 512

static int pwmfd = -1;

static void usage(char *argv[])
{
	fprintf(stderr, "%s %s <filepath>\n", argv[0], argv[1]);
}

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

void main_moppy(void)
{
	while(true)
	{
		printf("Running moppy!!!\n");

		/********** Audio recorder **********/
		FILE *f = NULL;
		f = fopen("/media/0/record.wav", "wb");
		if (!f) {
			perror("fopen()");
			goto err;
		}
	
		if (media_record_init() != RECORD_OK) {
			fprintf(stderr, "media_record_init error\n");
			goto err;
		}
	
		if (media_record_set_config(2, 22050, PCM_FORMAT_S16_LE, MEDIA_FORMAT_WAV) != RECORD_OK) {
			fprintf(stderr, "media_record_set_config error\n");
			goto err;
		}
	
		if (media_record_prepare() != RECORD_OK) {
			fprintf(stderr, "media_record_prepare error\n");
			goto err;
		}

		codec_start();
	
		if (media_record(fileno(f)) != RECORD_OK) {
			fprintf(stderr, "media_record error\n");
			goto err;
		}
	
		printf("Voice recording for 3 seconds...\n");
		up_mdelay(3000);
	
		media_stop_record();
		fclose(f);

		err:
		codec_stop();
		if (f) fclose(f);

		printf("Recorded\n");
		printf("---------------------------------\n");


		/********** Socket info **********/
		int sock;
		struct sockaddr_in server;

		sock = socket(AF_INET, SOCK_STREAM, 0);
		if (sock == -1)
		{
			printf("Could not create socket\n");
		}
		printf("Socket created\n");

		server.sin_addr.s_addr = inet_addr(HOST);
		server.sin_family = AF_INET;
		server.sin_port = htons(PORT);

		// connect to remote server
		if (connect(sock , (struct sockaddr *)&server , sizeof(server)) < 0)
		{
			perror("connect failed. Error");
			//return 1;
		}
		printf("Socket connected\n");


		/********** Sending file size **********/
		// getting file size
		long file_size = 0;
		char file_path[] = "/media/0/record.wav";
		FILE *fp;
		fp = fopen(file_path, "rb");
		if (fp == NULL){
			printf("File not Exist\n");
			exit(1);
		}
		fseek(fp, 0, SEEK_END);
		file_size = ftell(fp);
		printf("Sent file size >> %d\n", file_size);

		// length of integer(file size)
		int len_digits = 0;
		len_digits = snprintf(NULL, 0, "%i", file_size);

		// integer to string
		char size_msg[len_digits];
		sprintf(size_msg, "%d", file_size);

		// sending file size
		int sendBytes = 0;
		sendBytes = send(sock, size_msg, sizeof(size_msg), 0);
	

		/********** Sending file data **********/
		int totalBufferNum = 0;
		int BufferNum = 0;
		long totalSendBytes = 0;
		char buf[BUFF_SIZE];
		int check = 0;	

		totalBufferNum = file_size / sizeof(buf) + 1; 
		memset(buf, 0x00, BUFF_SIZE);
		fseek(fp, 0, SEEK_SET);

		printf("Sending file...\n");
		while ((sendBytes = fread(buf, sizeof(char), sizeof(buf), fp))>0) {
			check = send(sock, buf, sendBytes, 0);
			if (check < 0){
				printf("here~\n");
				printf("  %d  \n", check);
				break;
			}
			BufferNum++;
			totalSendBytes += sendBytes;
			//printf("In progress: %d/%dByte(s) [%d%%]\n", totalSendBytes, file_size, ((BufferNum * 100) / totalBufferNum));
		}

		fclose(fp);
		printf("File sent\n");
		printf("---------------------------------\n");


		/********** Receiving file **********/
		int recv_file_size;
		int readBytes;
		long totalReadBytes;

		totalReadBytes = 0;

		memset(buf, 0x00, BUFF_SIZE);

		readBytes = recv(sock, buf, BUFF_SIZE, 0);
		recv_file_size = atol(buf);
		printf("Receivced file size >> %d\n", recv_file_size);


		fp = fopen("/media/0/play.wav", "wb");
		if (fp == NULL){
			printf("File not Exist\n");
			exit(1);
		}
		
		printf("Receiving file...\n");
		while (totalReadBytes != recv_file_size) {
			readBytes = recv(sock, buf, BUFF_SIZE, 0);
			totalReadBytes += readBytes;
			//printf("In progress: %d/%dByte(s) [%d%%]\n", totalReadBytes, recv_file_size, ((totalReadBytes * 100) / recv_file_size));
			fwrite(buf, sizeof(char), readBytes, fp);
		}
		fclose(fp);
		printf("File received\n");


		/********** Audio player **********/
		printf("Playing audio...\n");

		uint8_t vol1 = 16;
		f = fopen("/media/0/play.wav", "rb");
		if (!f) {
			perror("fopen()");
			return;
		}
		media_play_init();

		codec_start();
	
		if (media_play(fileno(f), MEDIA_FORMAT_WAV) != MEDIA_OK) {
			fprintf(stderr, "media_play error!\n");
		}
	
		media_set_vol(vol1);
		while (media_is_playing());

		media_stop_play();

		codec_stop();

		fclose(f);
	
		sleep(1);

		//closesocket(sock);
		//printf("Closed socket\n");

		printf("=================================\n");
	}
}


