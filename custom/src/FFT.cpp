#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <getopt.h>

typedef float FLOAT;

#include "ffft/FFTReal.h"
#include "FFTWindow.h"

#define MAXPTS 65536

void GetSampleRaw(FLOAT *Left, FLOAT *Right, int Width)
{
	const FLOAT i2f = 0.0000000004656612873077392578125;
	int iVal[2] = { 0, 0 };
	FLOAT *pV[2];
	int i;
	
	pV[0] = Left;
	pV[1] = Right;

	for (i=0; i<2; i++)
	{
		if (Width==32)
		{
			iVal[i] |= getchar();
			iVal[i] |= (getchar() << 8);
		}
		iVal[i] |= (getchar() << 16);
		iVal[i] |= (getchar() << 24);

		*pV[i] = iVal[i] * i2f;
	}
}

int main(int argc, char **argv)
{
	FLOAT SampRate = 48000.0;				// r
	int nAvg = 1;							// n
	int nPts = MAXPTS/4;					// p
	FLOAT Skip = 0.0;						// s
	int Width = 32;							// 2
	int LeftOnly = 0;						// L
	int RightOnly = 0;						// R
	int nEat = 0;							// e

	int opt;
	
	while ((opt = getopt(argc, argv, "r:n:p:s:v2LRe:")) != -1)
	{
		switch (opt)
		{
			case 'r':
				SampRate = atof(optarg);
				break;
			case 'p':
				nPts = atoi(optarg);
				break;
			case 'n':
				nAvg = atoi(optarg);
				break;
			case 's':
				Skip = atof(optarg);
				break;
			case '2':
				Width = 16;
				break;
			case 'L':
				LeftOnly = 1;
				RightOnly = 0;
				break;
			case 'R':
				RightOnly = 1;
				LeftOnly = 0;
				break;
			case 'e':
				nEat = atoi(optarg);
				break;
			case ':':
				fprintf(stderr, "Option '%c' requires value\n\n", optopt);
			case '?':
				if (opt=='?')
					fprintf(stderr, "Option '%c' unrecognized\n\n", optopt);
			case 'h':
				printf("THDn [-h] [-r SAMPRATE] [-p PTS] [-n NAVGS] [-s SKIP] [-m MINLEFT] [-M MINRIGHT] [-f FREQLEFT] [-F FREQRIGHT] [-2] [-w FREQWIDTH]\n"
				       "  -h                Print usage\n"
				       "  -r SAMPRATE       Set sample rate (default: 48000)\n"
				       "  -2                16 bits per sample instead of 32\n"
				       "  -p PTS            Number of samples in FFT (power of 2) (default: 16384)\n"
				       "  -n NAVGS          Number of averages (default: 1)\n"
				       "  -s SKIP           Number of seconds of data to discard at beginning of test (not counted in duration) (default: 0)\n"
				       "  -e EAT            Discard number of bytes of data at beginning of test (default: 0)\n"
				       "  -L                Test Left channel only\n"
				       "  -R                Test Right channel only\n");
				return 1;
		}
	}

	{
		int i;
		for (i=0; i<nEat; i++)
			getchar();
	}

	{
		int nSkip;
		static FLOAT x[2][MAXPTS];
		static FLOAT f[MAXPTS];
		static FLOAT fAvg[2][MAXPTS/2+1];
		int iChan;
		int iAvg;
		int iSamp;
		ffft::FFTReal <FLOAT> fft(nPts);

		nSkip = (int)(Skip * SampRate + 0.5);
		
		for (iSamp=0; iSamp<=nPts; iSamp++)
		{
			fAvg[0][iSamp] = 0;
			fAvg[1][iSamp] = 0;
		}
		
		for (iSamp=0; iSamp<nSkip; iSamp++)
		{
			FLOAT v[2];
			GetSampleRaw(&v[0], &v[1], Width);
		}
	
		for (iAvg=0; iAvg<nAvg; iAvg++)
		{
			for (iSamp=0; iSamp<nPts; iSamp++)
			{
				GetSampleRaw(&x[0][iSamp],
				             &x[1][iSamp],
				             Width);
			}
			for (iChan=0; iChan<2; iChan++)
			{
				FFTWindow(x[iChan],
				          nPts,
				          HANNING_WINDOW);

				fft.do_fft(f, x[iChan]);

				for (iSamp=0; iSamp<=nPts/2; iSamp++)
				{
					if (iSamp==0 || iSamp==nPts/2)
						fAvg[iChan][iSamp] += f[iSamp]*f[iSamp]/(nPts*(FLOAT)nPts*nAvg);
					else
					{
						fAvg[iChan][iSamp] += (f[iSamp]*f[iSamp]+f[iSamp+nPts/2]*f[iSamp+nPts/2])/(nAvg*(FLOAT)nPts*nPts/4);
					}
				}
			}
		}

		for (iSamp=0; iSamp<=nPts/2; iSamp++)
		{
			for (iChan=0; iChan<2; iChan++)
			{
				fAvg[iChan][iSamp] = sqrt(fAvg[iChan][iSamp]);
			}
		}
		
		if (LeftOnly)
		{
			printf("Freq (Hz),Left\n");
			for (iSamp=(int)(20/(SampRate/nPts)+0.5); iSamp<=(int)(20000/(SampRate/nPts)+0.5); iSamp++)
			{
				printf("%8.2f,%10.8f\n",
				       iSamp*SampRate/nPts,
				       fAvg[0][iSamp]);
			}
		}
		else if (RightOnly)
		{
			printf("Freq (Hz),Right\n");
			for (iSamp=(int)(20/(SampRate/nPts)+0.5); iSamp<=(int)(20000/(SampRate/nPts)+0.5); iSamp++)
			{
				printf("%8.2f,%10.8f\n",
				       iSamp*SampRate/nPts,
				       fAvg[1][iSamp]);
			}
		}
		else
		{
			printf("Freq (Hz),Left,Right\n");
			for (iSamp=(int)(20/(SampRate/nPts)+0.5); iSamp<=(int)(20000/(SampRate/nPts)+0.5); iSamp++)
			{
				printf("%8.2f,%10.8f,%10.8f\n",
				       iSamp*SampRate/nPts,
				       fAvg[0][iSamp],
				       fAvg[1][iSamp]);
			}
		}
	
		return 0;
	}
}