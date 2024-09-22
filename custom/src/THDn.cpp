#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <getopt.h>

typedef float FLOAT;

#include "ffft/FFTReal.h"
#include "FFTWindow.h"

#define MAXPTS (1<<18)

#define HIPASS  (48000/10)
FLOAT HiPassData[2][HIPASS];
FLOAT HiPassAvg[2];
int HiPassCnt = 0;

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

void GetSample(FLOAT *Left, FLOAT *Right, int Width)
{
	static int fFirst = 1;
	FLOAT *pV[2];
	int i;
	FLOAT v[2];
	
	pV[0] = Left;
	pV[1] = Right;

	if (fFirst)
	{
		for (i=0; i<HIPASS-1; i++)
		{
			GetSampleRaw(&HiPassData[0][i],
			             &HiPassData[1][i],
			             Width);
			HiPassAvg[0] += HiPassData[0][i];
			HiPassAvg[1] += HiPassData[1][i];
		}
		HiPassCnt = HIPASS-1;
		
		fFirst = 0;
	}
	
	GetSampleRaw(&v[0], &v[1], Width);

	for (i=0; i<2; i++)
	{
		HiPassAvg[i] += (v[i]-HiPassData[i][HiPassCnt]);
		HiPassData[i][HiPassCnt] = v[i];
	
		*pV[i] = HiPassData[i][(HiPassCnt+HIPASS/2)%HIPASS]-HiPassAvg[i]/HIPASS;
	}
	
	HiPassCnt = (HiPassCnt+1) % HIPASS;
}

int main(int argc, char **argv)
{
	FLOAT SampRate = 48000.0;				// r
	int nAvg = 1;							// n
	int nPts = MAXPTS/4;					// p
	FLOAT Skip = 0.0;						// s
	int Verbose = 0;						// v
	int Width = 32;							// 2
	int fWidth = 6;							// w
	int LeftOnly = 0;						// L
	int RightOnly = 0;						// R
	int nEat = 0;							// e

	FLOAT Freq[2] = { 0, 0 };				// f F
	FLOAT Max[2] = { 0, 0 };				// x X
	
	int FailFlag = 0;

	int opt;
	
	while ((opt = getopt(argc, argv, "r:n:p:s:v2x:X:f:F:w:LRe:")) != -1)
	{
		switch (opt)
		{
			case 'v':
				Verbose = 1;
				break;
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
			case 'x':
				Max[0] = atof(optarg);
				break;
			case 'X':
				Max[1] = atof(optarg);
				break;
			case 'f':
				Freq[0] = atof(optarg);
				break;
			case 'F':
				Freq[1] = atof(optarg);
				break;
			case 'w':
				fWidth = atoi(optarg);
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
				       "  -R                Test Right channel only\n"
				       "  -x MAXLEFT        Maximum allowable THD+n on left as %% (default:1)\n"
				       "  -X MAXRIGHT       Maximum allowable THD+n on right as %% (default:1)\n"
				       "  -f FREQLEFT       Left signal frequency (default:0 (auto))\n"
				       "  -F FREQRIGHT      Right signal frequency (default:0 (auto))\n"
				       "  -w FREQWIDTH      Frequency lines on either side of freq to include in freq (default:6)\n");
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
		int iFreq[2];
		FLOAT v[2];
		int iChan;
		int iAvg;
		int iSamp;
		FLOAT Sig[2] = { 0, 0 };
		FLOAT Noise[2] = { 0, 0 };
		FLOAT THDn[2];
		ffft::FFTReal <FLOAT> fft(nPts);

		nSkip = (int)(Skip * SampRate + 0.5);
		
		for (iSamp=0; iSamp<=nPts; iSamp++)
		{
			fAvg[0][iSamp] = 0;
			fAvg[1][iSamp] = 0;
		}
		
		for (iSamp=0; iSamp<nSkip; iSamp++)
		{
			GetSample(&v[0], &v[1], Width);
		}
	
		for (iAvg=0; iAvg<nAvg; iAvg++)
		{
			for (iSamp=0; iSamp<nPts; iSamp++)
			{
				GetSample(&x[0][iSamp],
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

		for (iChan=0; iChan<2; iChan++)
		{
			if (Freq[iChan]!=0)
			{
				iFreq[iChan] = (int)(Freq[iChan]/(SampRate/nPts)+0.5);
			}
			else
			{
				float mx = 0;
				for (iSamp=(int)(20/(SampRate/nPts)+0.5); iSamp<=nPts/2; iSamp++)
				{
					if (fAvg[iChan][iSamp] > mx)
					{
						mx = fAvg[iChan][iSamp];
						iFreq[iChan] = iSamp;
					}
				}
			}
		}
		
		for (iSamp=(int)(20/(SampRate/nPts)+0.5); iSamp<=nPts/2; iSamp++)
		{
			for (iChan=0; iChan<2; iChan++)
			{
				if (iSamp >= iFreq[iChan]-fWidth && iSamp <= iFreq[iChan]+fWidth)
					Sig[iChan] += fAvg[iChan][iSamp];
				else
					Noise[iChan] += fAvg[iChan][iSamp];
			}
		}
		
		for (iChan=0; iChan<2; iChan++)
		{
			Noise[iChan] = sqrt(Noise[iChan]);
			if (Sig[iChan] > 0.0)
			{
				Sig[iChan] = sqrt(Sig[iChan]);
				THDn[iChan] = 100*Noise[iChan]/Sig[iChan];
			}
			else
			{
				Sig[iChan] = 0;
				THDn[iChan] = 100;
			}
		}
		
		if (Verbose)
		{
			if (!RightOnly)
				printf("Left   Signal: %7.5f   HD+n: %7.5f\n", Sig[0], Noise[0]);
			if (!LeftOnly)
				printf("Right  Signal: %7.5f   HD+n: %7.5f\n", Sig[1], Noise[1]);
			if (!RightOnly)
				printf("Left  THD+n: %7.3f%%\n",
				       THDn[0]);
			if (!LeftOnly)
				printf("Right THD+n: %7.3f%%\n",
				       THDn[1]);
		}
		else
		{
			if (LeftOnly)
				printf("%7.3f\n",
				       THDn[0]);
			else if (RightOnly)
				printf("%7.3f\n",
				       THDn[1]);
			else
				printf("%7.3f,%7.3f\n",
				       THDn[0],
				       THDn[1]);
		}

		if (LeftOnly)
		{
			if (THDn[0]>Max[0])
				FailFlag += 2;
		}
		else if (RightOnly)
		{
			if (THDn[1]>Max[1])
				FailFlag += 8;
		}
		else
		{
			if (THDn[0]>Max[0])
				FailFlag += 2;
			if (THDn[1]>Max[1])
				FailFlag += 8;
		}
	
		return FailFlag;
	}
}