#include <stdio.h>
#include <stdlib.h>
#include <fcntl.h>
#include <tinyara/pwm.h>

#include <media/media_player.h>

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

//void mediaplayer_main(int argc, char *argv[])
void main_player(void)
{
	FILE *f;
	uint8_t vol1 = 30;
	f = fopen("/media/0/test1.wav", "rb");
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
	
	printf("finished!!\n");
	
	codec_stop();
		
	fclose(f);
}
