#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>

#include <stdio.h>
#include <string.h>
#include <sys/socket.h>

#include <stdlib.h>
#include <errno.h>

#define PORT 7001
//#define IP "112.221.113.29"
#define IP "192.168.0.10"
#define BUFF_SIZE 512

void main_socket(void)
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

	server.sin_addr.s_addr = inet_addr(IP);
	server.sin_family = AF_INET;
	server.sin_port = htons(PORT);

	// connect to remote server
	if (connect(sock , (struct sockaddr *)&server , sizeof(server)) < 0)
	{
		perror("connect failed. Error");
		//return 1;
	}
	puts("Connected\n");

	/********** Sending file **********/
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
	printf("file size >> %d\n", file_size);

	// length of integer(file size)
	int len_digits = 0;
	len_digits = snprintf(NULL, 0, "%i", file_size);

	// integer to string
	char size_msg[len_digits];
	sprintf(size_msg, "%d", file_size);

	// sending file size
	int sendBytes = 0;
	sendBytes = send(sock, size_msg, sizeof(size_msg), 0);
	
	// sending file
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
		printf("In progress: %d/%dByte(s) [%d%%]\n", totalSendBytes, file_size, ((BufferNum * 100) / totalBufferNum));
	}

	fclose(fp);
	printf("File sent\n");
	puts("=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=\n");

	/********** Receiving file **********/
	int recv_file_size;
	int readBytes;
	long totalReadBytes;

	memset(buf, 0x00, BUFF_SIZE);

	fp = fopen("/media/0/play.wav", "wb");
	if (fp == NULL){
		printf("File not Exist");
		exit(1);
	}

	readBytes = recv(sock, buf, BUFF_SIZE, 0);
	recv_file_size = atol(buf);
	totalReadBytes = 0;
	
	printf("file size >> %d\n", recv_file_size);

	while (totalReadBytes != recv_file_size) {
		readBytes = recv(sock, buf, BUFF_SIZE, 0);
		totalReadBytes += readBytes;
		printf("In progress: %d/%dByte(s) [%d%%]\n", totalReadBytes, recv_file_size, ((totalReadBytes * 100) / recv_file_size));
		fwrite(buf, sizeof(char), readBytes, fp);
	}
	fclose(fp);
	printf("File received\n");

	closesocket(sock);
	printf("Closed socket\n");
}


