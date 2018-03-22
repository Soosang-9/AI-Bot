#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>

#include <stdio.h>
#include <string.h>
#include <sys/socket.h>

#include <stdlib.h>
#include <errno.h>

#include <netutils/netlib.h>

#define PORT 7001
//#define HOST "112.221.113.29"
#define HOST "192.168.0.134"
#define BUFF_SIZE 512


void main_test2(void)
{
	/********** Socket info **********/
	int sock;
	struct sockaddr_in server;

	sock = socket(AF_INET, SOCK_STREAM, 0);
	if (sock == -1)
	{
		printf("Could not create socket");
	}
	puts("Socket created");

	server.sin_addr.s_addr = inet_addr(HOST);
	server.sin_family = AF_INET;
	server.sin_port = htons(PORT);

	// connect to remote server
	if (connect(sock , (struct sockaddr *)&server , sizeof(server)) < 0)
	{
		perror("connect failed. Error");
		//return 1;
	}
	puts("Connected");


	/********** Sending Device ID of ARTIK053 **********/
	uint8_t macId[6];
	netlib_getmacaddr("wl1", macId);

	char device_id[17];
	sprintf(device_id, "%02X:%02X:%02X:%02X:%02X:%02X", 
				((uint8_t *) macId)[0], ((uint8_t *) macId)[1],	
				((uint8_t *) macId)[2], ((uint8_t *) macId)[3],	
				((uint8_t *) macId)[4], ((uint8_t *) macId)[5]);
	//printf("Device ID >> %s\n", device_id);
	//printf("%d\n", strlen(device_id));

	char msg_format_DI[4+17] = "DI, ";
	strcat(msg_format_DI, device_id);
	printf("msg_format_DI >> %s\n", msg_format_DI);

	send(sock, msg_format_DI, sizeof(msg_format_DI), 0);


	/********** Return Checking Message of Sending Device ID **********/
/*
	char return_DI[2];

	//memset(return_DI, 0x00, sizeof(return_DI));
	recv(sock, return_DI, sizeof(return_DI), 0);

	//return_DI = atol(return_DI);
	printf("return_DI >> %s\n", return_DI);

	if(!strcmp(return_DI, "OK"))
	{
		puts("good");
	}
*/

	/********** Sending File Size **********/
	// getting file size
	long file_size = 0;
	char file_path[] = "/media/0/test1.wav";
	FILE *fp;
	fp = fopen(file_path, "rb");
	if (fp == NULL){
		printf("File not Exist");
		exit(1);
	}
	fseek(fp, 0, SEEK_END);
	file_size = ftell(fp);
	//printf("File Size >> %d\n", (file_size));

	// length of integer(file size)
	int len_digits = 0;
	len_digits = snprintf(NULL, 0, "%i", file_size);

	// integer to string
	char size_msg[len_digits];
	sprintf(size_msg, "%d", file_size);

	// message format
	char msg_format_FS[4 + len_digits];
	strcpy(msg_format_FS, "FS, ");	
	strcat(msg_format_FS, size_msg);
	printf("msg_format_FS >> %s\n", msg_format_FS);

	// sending file size
	send(sock, msg_format_FS, sizeof(msg_format_FS), 0);


	/********** Return Checking Message of Sending Device ID **********/
/*
	char return_FS[2];

	//memset(return_FS, 0x00, sizeof(return_FS));
	recv(sock, return_FS, sizeof(return_FS), 0);

	//return_FS = atol(return_FS);
	printf("return_FS >> %s\n", return_FS);

	if(!strcmp(return_FS, "OK"))
	{
		puts("good");
	}
*/	

	/********** Sending File Data **********/
	char msg_format_FD[2];
	strcpy(msg_format_FD, "FD");
	printf("msg_format_FD >> %s\n", msg_format_FD);
	send(sock, msg_format_FD, sizeof(msg_format_FD), 0);

	int sendBytes = 0;
	int totalBufferNum = 0;
	int BufferNum = 0;
	long totalSendBytes = 0;
	char buf[BUFF_SIZE];
	int check = 0;

	totalBufferNum = file_size / sizeof(buf) + 1; 
	memset(buf, 0x00, BUFF_SIZE);
	fseek(fp, 0, SEEK_SET);

	while ((sendBytes = fread(buf, sizeof(char), sizeof(buf), fp))>0) {
		check = send(sock, buf, sendBytes, 0);
		if (check < 0){
			puts("here~ ");
			printf("  %d  \n", check);
			break;
		}
		BufferNum++;
		totalSendBytes += sendBytes;
		//printf("In progress: %d/%dByte(s) [%d%%]\n", totalSendBytes, file_size, ((BufferNum * 100) / totalBufferNum));
	}

	fclose(fp);
	printf("File sent\n");
	puts("=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=\n");


	/********** Receiving File Size **********/
	char recv_file_size[20];

	recv(sock, recv_file_size, sizeof(recv_file_size), 0);

	printf("recv_file_size >> %s\n", recv_file_size);
	
	char *ptr = strtok(recv_file_size, ", ");
	printf("slice >> %s\n", ptr[0]);
	printf("slice >> %s\n", ptr[1]);
	printf("slice >> %s\n", ptr[2]);

	if(!strcmp(recv_file_size, "OK"))
	{
		puts("good");
	}
/*
	int recv_file_size;

	memset(buf, 0x00, BUFF_SIZE);

	recv(sock, buf, BUFF_SIZE, 0);
	recv_file_size = atol(buf);
	
	printf("Receiving File size >> %d\n", recv_file_size);
*/
	/********** Receiving File Data **********/
/*
	int readBytes;
	long totalReadBytes;

	totalReadBytes = 0;

	fp = fopen("/media/0/play.wav", "wb");
	if (fp == NULL){
		printf("File not Exist");
		exit(1);
	}

	while (totalReadBytes != recv_file_size) {
		readBytes = recv(sock, buf, BUFF_SIZE, 0);
		totalReadBytes += readBytes;
		//printf("In progress: %d/%dByte(s) [%d%%]\n", totalReadBytes, recv_file_size, ((totalReadBytes * 100) / recv_file_size));
		fwrite(buf, sizeof(char), readBytes, fp);
	}
	fclose(fp);
	printf("File received\n");
*/

	closesocket(sock);
	printf("Closed socket\n");
}


