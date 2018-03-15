#include <stdio.h>
#include <stdlib.h>
#include <fcntl.h>
#include <tinyara/pwm.h>
#include <apps/graphics/gui.h>

#include <media/media_recorder.h>
#include <media/media_utils.h>

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

void main_recorder(void)
{
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
	
	printf("Recording... Wait 3 seconds\n");
	up_mdelay(3000);

	printf("Finished!\n");
	
	media_stop_record();
	fclose(f);
	
	printf("record end!!\n");
	
err:
	codec_stop();
	if (f) fclose(f);
}
