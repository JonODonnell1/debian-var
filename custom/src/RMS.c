#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <getopt.h>

typedef float FLOAT;

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
	FLOAT Duration = 1.0;					// d
	FLOAT Skip = 0.0;						// s
	int Verbose = 0;						// v
	int Width = 32;							// 2
	int HiPass = 0;							// H
	int LeftOnly = 0;						// L
	int RightOnly = 0;						// R
	int nEat = 0;							// e

	FLOAT percentFS_min[2] = { 0, 0 };		// m M
	FLOAT percentFS_max[2] = { 100, 100};	// x X
	
	int nDuration;
	int nSkip;
	FLOAT v[2];
	FLOAT sum2[2] = { 0, 0 };
	FLOAT RMS[2];
	int i;
	
	int FailFlag = 0;
	
	int opt;
	
	while ((opt = getopt(argc, argv, "r:d:s:v2m:M:x:X:HLRe:")) != -1)
	{
		switch (opt)
		{
			case 'v':
				Verbose = 1;
				break;
			case 'r':
				SampRate = atof(optarg);
				break;
			case 'd':
				Duration = atof(optarg);
				break;
			case 's':
				Skip = atof(optarg);
				break;
			case 'm':
				percentFS_min[0] = atof(optarg);
				break;
			case 'M':
				percentFS_min[1] = atof(optarg);
				break;
			case 'x':
				percentFS_max[0] = atof(optarg);
				break;
			case 'X':
				percentFS_max[1] = atof(optarg);
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
			case 'H':
				HiPass = 1;
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
				printf("RMS [-h] [-r SAMPRATE] [-d DURATION] [-s SKIP] [-m MINLEFT] [-M MINRIGHT] [-x MAXLEFT] [-X MAXRIGHT] [-H] [-2]\n"
				       "  -h                Print usage\n"
				       "  -r SAMPRATE       Set sample rate (default: 48000)\n"
				       "  -2                16 bits per sample instead of 32\n"
				       "  -d DURATION       Test duration in seconds (default: 1)\n"
				       "  -s SKIP           Number of seconds of data to discard at beginning of test (not counted in duration) (default: 0)\n"
				       "  -e EAT            Discard number of bytes of data at beginning of test (default: 0)\n"
				       "  -L                Test Left channel only\n"
				       "  -R                Test Right channel only\n"
				       "  -m MINLEFT        Minimum allowable RMS amplitude on left as %% FS (default:0)\n"
				       "  -M MINRIGHT       Minimum allowable RMS amplitude on right as %% FS (default:0)\n"
				       "  -x MAXLEFT        Maximum allowable RMS amplitude on left as %% FS (default:100)\n"
				       "  -X MAXRIGHT       Maximum allowable RMS amplitude on right as %% FS (default:100)\n"
				       "  -H                Hi-Pass filter data first\n\n");
				return 1;
		}
	}
	
	for (i=0; i<nEat; i++)
		getchar();
	
	nSkip = (int)(Skip * SampRate + 0.5);
	nDuration = (int)(Duration * SampRate + 0.5);
	
	for (i=0; i<nSkip; i++)
	{
		if (HiPass)
			GetSample(&v[0], &v[1], Width);
		else
			GetSampleRaw(&v[0], &v[1], Width);
	}

	for (i=0; i<nDuration; i++)
	{
		if (HiPass)
			GetSample(&v[0], &v[1], Width);
		else
			GetSampleRaw(&v[0], &v[1], Width);

		sum2[0] += v[0]*v[0]/nDuration;
		sum2[1] += v[1]*v[1]/nDuration;
	}
	
	RMS[0] = 100*sqrt(sum2[0]);
	RMS[1] = 100*sqrt(sum2[1]);
	
	if (LeftOnly)
	{
		if (RMS[0]<percentFS_min[0])
			FailFlag += 1;
		if (RMS[0]>percentFS_max[0])
			FailFlag += 2;
		printf("%f\n", RMS[0]);
	}
	else if (RightOnly)
	{
		if (RMS[1]<percentFS_min[1])
			FailFlag += 4;
		if (RMS[1]>percentFS_max[1])
			FailFlag += 8;
		printf("%f\n", RMS[1]);
	}
	else
	{
		if (RMS[0]<percentFS_min[0])
			FailFlag += 1;
		if (RMS[0]>percentFS_max[0])
			FailFlag += 2;
		if (RMS[1]<percentFS_min[1])
			FailFlag += 4;
		if (RMS[1]>percentFS_max[1])
			FailFlag += 8;
		printf("%f,%f\n", RMS[0], RMS[1]);
	}
	

	return FailFlag;
}
