#include <stdlib.h>
#include <stdio.h>
#include <math.h>
#include <getopt.h>
#include <time.h>

typedef double FLOAT;

#include "pink.h"

//#define WHITE_HIPASS  (48000/10)

int main(int argc, char **argv)
{
	// setup parameters
	FLOAT Volume = 0.0;					// V
	int SampRate = 48000;				// r
	int Duration = 1;					// d
	int nRepeat = 1;					// n
	int DutyCycle = 100;				// D
	int AlternateLeftRight = 0;			// D with negative value
	int Verbose = 0;					// v
	int Width = 32;						// 2

	int Pink[2] = { 0, 0 };				// p P
	int White[2] = { 0, 0 };			// w W

	int Sine[2] = { 0, 0 };
	int BiDir = 0;						// b
	int Log = 0;						// l
	int FreqStart[2] = { 0, 0 };		// f F
	int FreqEnd[2] = { 0, 0 };			// e E
	
	int nSkipStart[2];
	int nSkipEnd[2];
	FLOAT Phase[2] = { 0, 0 };
	const FLOAT _2pi = 6.283185307179586476925286766559;
	enum { modeFixed, modeLin, modeLinBiDir, modeLog, modeLogBiDir } Mode[2];
	FLOAT LogFreqStart[2];
	FLOAT LogFreqEnd[2];
	
	PinkNoise PinkData[2];
	
//	int WhiteData[2][WHITE_HIPASS];
//	int WhiteSum[2];
//	int WhiteLoc[2];

	int iRepeat;
	int iSamp;
	int iChan;
	int nSamp;
	int nSampOn;
	FLOAT VolumeScale;
	
	int opt;
	
	while ((opt = getopt(argc, argv, "V:hvblr:d:f:F:e:E:n:D:2pPwW")) != -1)
	{
		switch (opt)
		{
			case 'V':
				Volume = atof(optarg);
				break;
			case 'v':
				Verbose = 1;
				break;
			case 'b':
				BiDir = 1;
				break;
			case 'l':
				Log = 1;
				break;
			case 'r':
				SampRate = atoi(optarg);
				break;
			case 'd':
				Duration = atoi(optarg);
				break;
			case 'f':
				FreqStart[0] = atoi(optarg);
				if (FreqStart[0] != 0)
				{
					Sine[0] = 1;
					Pink[0] = White[0] = 0;
				}
				break;
			case 'F':
				FreqStart[1] = atoi(optarg);
				if (FreqStart[1] != 0)
				{
					Sine[1] = 1;
					Pink[1] = White[1] = 0;
				}
				break;
			case 'e':
				FreqEnd[0] = atoi(optarg);
				if (FreqEnd[0] != 0)
				{
					Sine[0] = 1;
					Pink[0] = White[0] = 0;
				}
				break;
			case 'E':
				FreqEnd[1] = atoi(optarg);
				if (FreqEnd[1] != 0)
				{
					Sine[1] = 1;
					Pink[1] = White[1] = 0;
				}
				break;
			case 'n':
				nRepeat = atoi(optarg);
				break;
			case 'D':
				DutyCycle = atoi(optarg);
				if (DutyCycle < 0)
				{
					AlternateLeftRight = 1;
					DutyCycle = -DutyCycle;
				}
				break;
			case '2':
				Width = 16;
				break;
			case 'p':
				Pink[0] = 1;
				Sine[0] = White[0] = 0;
				break;
			case 'P':
				Pink[1] = 1;
				Sine[1] = White[1] = 0;
				break;
			case 'w':
				White[0] = 1;
				Sine[0] = Pink[0] = 0;
				break;
			case 'W':
				White[1] = 1;
				Sine[1] = Pink[1] = 0;
				break;
			case ':':
				fprintf(stderr, "Option '%c' requires value\n\n", optopt);
			case '?':
				if (opt=='?')
					fprintf(stderr, "Option '%c' unrecognized\n\n", optopt);
			case 'h':
				printf("SinGen [-h] [-r SAMPRATE] [-d DURATION] [-n REPEATS] [-D DUTYCYCLE] [-2] [-w] [-W] [-p] [-P] [-f LEFTFREQ] [-F RIGHTFREQ] [-e LEFTENDFREQ] [-E RIGHTENDFREQ] [-b] [-l]\n"
				       "  -h                Print usage\n"
				       "  -V VOLUME         Set volume in dB (default: 0 (max))\n"
				       "  -r SAMPRATE       Set sample rate (default: 48000, min: 1000, max:200000)\n"
				       "  -d DURATION       Set cycle duration in seconds (default: 1, min: 1, max: 40000)\n"
				       "  -n REPEATS        Set number of cycles >=1 (default:1, min: 1, max:2000000000)\n"
				       "  -D DUTYCYCLE      Set duty cycle of output 1-100 (default: 100, min: 1, max: 100)\n"
				       "                      (-1)-(-100) to have duty cycle alternate left and right\n"
				       "  -2                Use 16 bit output instead of 32\n"
				       "  -w                Generate white noise (instead of sine/sweep/pink) on left channel output\n"
				       "  -W                Generate white noise (instead of sine/sweep/pink) on right channel output\n"
				       "  -p                Generate pink noise (instead of sine/sweep/white) on left channel output\n"
				       "  -P                Generate pink noise (instead of sine/sweep/white) on right channel output\n"
				       "  -f LEFTFREQ       Set frequency of left channel output (default: 440, min: 1, max: SAMPRATE/2-1)\n"
				       "  -F RIGHTFREQ      Set frequency of right channel output (default: 440), min: 1, max: SAMPRATE/2-1\n"
				       "  -e LEFTENDFREQ    Set frequency of left channel sweep end (default: 0 [no sweep], min: 1, max: SAMPRATE/2-1)\n"
				       "  -E RIGHTENDFREQ   Set frequency of right channel sweep end (default: 0 [no sweep]), min: 1, max: SAMPRATE/2-1\n"
				       "  -b                Set bi-directional sweep mode\n"
				       "  -l                Set log frequency sweep\n\n");
				       
				printf("Sample:\n"
				       "  # Output log sweep from 20Hz to 20kHz taking 30 seconds on left speaker and constant 440Hz on right speaker\n"
				       "  SinGen -d 30 -f 20 -e 20000 -F 440 -l | gst-launch fdsrc ! audio/x-raw-int, rate=48000, channels=2, endianness=1234, width=16, depth=16, signed=true ! pulsesink\n");
				return 1;
		}
	}
	if (SampRate < 1000)
	{
		SampRate = 1000;
		Verbose = 1;
	}
	if (SampRate > 200000)
	{
		SampRate = 200000;
		Verbose = 1;
	}
	if (Duration < 1)
	{
		Duration = 1;
		Verbose = 1;
	}
	if (Duration > 40000)
	{
		Duration = 40000;
		Verbose = 1;
	}
	if (nRepeat < 1)
	{
		nRepeat = 1;
		Verbose = 1;
	}
	if (nRepeat > 2000000000)
	{
		nRepeat = 2000000000;
		Verbose = 1;
	}
	if (DutyCycle < 1)
	{
		DutyCycle = 1;
		Verbose = 1;
	}
	if (DutyCycle > 100)
	{
		DutyCycle = 100;
		Verbose = 1;
	}
	if (Sine[0] == 0)
	{
		FreqStart[0] = FreqEnd[0] = 0;
	}
	else
	{
		if (FreqStart[0] < 1)
		{
			FreqStart[0] = 1;
			Verbose = 1;
		}
		if (FreqStart[0] > SampRate/2-1)
		{
			FreqStart[0] = SampRate/2-1;
			Verbose = 1;
		}
		if (FreqEnd[0] < 1)
		{
			FreqEnd[0] = FreqStart[0];
//			Verbose = 1;
		}
		if (FreqEnd[0] > SampRate/2-1)
		{
			FreqEnd[0] = SampRate/2-1;
			Verbose = 1;
		}
	}
	if (Sine[1] == 0)
	{
		FreqStart[1] = FreqEnd[1] = 0;
	}
	else
	{ 
		if (FreqStart[1] < 1)
		{
			FreqStart[1] = 1;
			Verbose = 1;
		}
		if (FreqStart[1] > SampRate/2-1)
		{
			FreqStart[1] = SampRate/2-1;
			Verbose = 1;
		}
		if (FreqEnd[1] < 1)
		{
			FreqEnd[1] = FreqStart[1];
//			Verbose = 1;
		}
		if (FreqEnd[1] > SampRate/2-1)
		{
			FreqEnd[1] = SampRate/2-1;
			Verbose = 1;
		}
	}
	
	nSamp = SampRate*Duration;     // overflow will occur if SampRate=48000 and Duration > 44739
	nSampOn = nSamp/100*DutyCycle; // Divide nSamp by 100 first to prevent int overflow.  nSamp is probably divisible by 100 anyway and a slight loss of precision on the duty cycle is acceptable.
	VolumeScale = pow(10.0, Volume / 20.0);

	for (iChan=0; iChan<2; iChan++)
	{
		if (Pink[iChan])
		{
			PinkNoiseInitialize(&PinkData[iChan]);
		}
		else if (White[iChan])
		{
//			int iAvg;
			srandom(time(NULL));
//			WhiteSum[iChan] = 0;
//			WhiteLoc[iChan] = 0;
//			for (iAvg = 0; iAvg<WHITE_HIPASS; iAvg++)
//			{
//				int v = (short)(random() & 0xFFFF);
//				WhiteData[iChan][iAvg] = v;
//				WhiteSum[iChan] += v;
//			}
		}
		else if (Sine[iChan])
		{
			if (FreqEnd[iChan] == 0)
				FreqEnd[iChan] = FreqStart[iChan];
			LogFreqStart[iChan] = log10((FLOAT)FreqStart[iChan]);
			LogFreqEnd[iChan] = log10((FLOAT)FreqEnd[iChan]);
			
			Mode[iChan] = (FreqStart[iChan]==FreqEnd[iChan] ? modeFixed :
			               (!Log ? (!BiDir ? modeLin : modeLinBiDir) : (!BiDir ? modeLog : modeLogBiDir)));
		}
		else
		{
			// silence
		}
	}
	
	if (Verbose)
		fprintf(stderr,
		        "GenSin\n"
		        "  Volume    = %g\n"
		        "  VolScale  = %g\n"
		        "  SampRate  = %d Hz\n"
		        "  Duration  = %d s\n"
		        "  Repeats   = %d\n"
		        "  Duty Cycle= %d%%\n"
		        "  Pink      = %5d    %5d\n"
		        "  Start     = %5d Hz %5d Hz\n"
		        "  End       = %5d Hz %5d Hz\n"
		        "  Bi-Dir    = %d\n"
		        "  Log       = %d\n",
		        Volume,
		        VolumeScale,
		        SampRate,
		        Duration,
		        nRepeat,
		        DutyCycle,
		        Pink[0], Pink[1],
		        FreqStart[0], FreqStart[1],
		        FreqEnd[0], FreqEnd[1],
		        BiDir,
		        Log);

	for (iRepeat=0; iRepeat<nRepeat; iRepeat++)
	{
		for (iSamp=0;iSamp<nSamp;iSamp++)
		{
			int v[2];    // 24-bit signed value
	
			for (iChan=0; iChan<2; iChan++)
			{
				int Alternate = (iChan==1 && AlternateLeftRight==1) ? 1 : 0;

				if ((Alternate==0 && iSamp>=nSampOn) ||
					(Alternate==1 && iSamp<nSampOn))
				{
					v[iChan] = 0;
				}
				else
				{
					if (Pink[iChan])
					{
						v[iChan] = PinkNoiseGenerate(&PinkData[iChan]) << 8;
					}
					else if (White[iChan])
					{
//						int i = (short)(random() & 0xFFFF);
//						WhiteSum[iChan] += (i - WhiteData[iChan][WhiteLoc[iChan]]);
//						WhiteData[iChan][WhiteLoc[iChan]] = i;
//						v[iChan] = WhiteData[iChan][(WhiteLoc[iChan]+WHITE_HIPASS/2) % WHITE_HIPASS] - WhiteSum[iChan]/WHITE_HIPASS;
//						WhiteLoc[iChan] = (WhiteLoc[iChan]+1) % WHITE_HIPASS;
						v[iChan] = ((int)((short)(random() & 0xFFFF))) << 8;
					}
					else if (Sine[iChan])
					{
						FLOAT DeltaPhase = 0;
						FLOAT Freq;
						
						switch (Mode[iChan])
						{
							case modeFixed:
								Freq = FreqStart[iChan];
								break;
								
							case modeLin:
								if (Alternate==0)
									Freq = FreqStart[iChan] + (FreqEnd[iChan]-FreqStart[iChan])*(FLOAT)iSamp/nSampOn;
								else
									Freq = FreqStart[iChan] + (FreqEnd[iChan]-FreqStart[iChan])*(FLOAT)(iSamp-nSampOn)/(nSamp-nSampOn);
								break;
		
							case modeLinBiDir:
								if (Alternate==0)
								{
									int i = (iSamp<=nSampOn/2 ? iSamp : nSampOn-iSamp);
									Freq = FreqStart[iChan] + (FreqEnd[iChan]-FreqStart[iChan])*(FLOAT)i/(nSampOn/2);
								}
								else
								{
									int i = ((iSamp-nSampOn)<=(nSamp-nSampOn)/2 ? (iSamp-nSampOn) : nSamp-iSamp);
									Freq = FreqStart[iChan] + (FreqEnd[iChan]-FreqStart[iChan])*(FLOAT)i/((nSamp-nSampOn)/2);
								}
								break;
		
							case modeLog:
								if (Alternate==0)
									Freq = pow(10.0, LogFreqStart[iChan] + (LogFreqEnd[iChan]-LogFreqStart[iChan])*iSamp/nSampOn);
								else
									Freq = pow(10.0, LogFreqStart[iChan] + (LogFreqEnd[iChan]-LogFreqStart[iChan])*(iSamp-nSampOn)/(nSamp-nSampOn));
								break;
		
							case modeLogBiDir:
								if (Alternate==0)
								{
									int i = (iSamp<=nSampOn/2 ? iSamp : nSampOn-iSamp);
									Freq = pow(10.0, LogFreqStart[iChan] + (LogFreqEnd[iChan]-LogFreqStart[iChan])*i/(nSampOn/2));
								}
								else
								{
									int i = ((iSamp-nSampOn)<=(nSamp-nSampOn)/2 ? (iSamp-nSampOn) : nSamp-iSamp);
									Freq = pow(10.0, LogFreqStart[iChan] + (LogFreqEnd[iChan]-LogFreqStart[iChan])*i/((nSamp-nSampOn)/2));
								}
								break;
						}
	
						DeltaPhase = _2pi*Freq/SampRate;
	
						v[iChan] = (int)(sin(Phase[iChan])*0x7FFFFF + 0.5);
						Phase[iChan] += DeltaPhase;
						if (Phase[iChan] >= _2pi)
							Phase[iChan] -= _2pi;
					}
					else
					{
						v[iChan] = 0;
					}
				}
				if (VolumeScale != 1.0)
					v[iChan] = (int)(v[iChan] * VolumeScale);
			}
			if (Width==32)
			{
				putchar(0x00);			// pad low byte
				putchar(v[0] & 0xFF);	// low byte of 24 bits calculated
			}
			putchar((v[0]>>8) & 0xFF);	// middle byte of 24 bits calculated
			putchar((v[0]>>16) & 0xFF);	// high byte of 24 bits calculated
			if (Width==32)
			{
				putchar(0x00);			// pad low byte
				putchar(v[1] & 0xFF);	// low byte of 24 bits calculated
			}
			putchar((v[1]>>8) & 0xFF);	// middle byte of 24 bits calculated
			putchar((v[1]>>16) & 0xFF);	// high byte of 24 bits calculated

//			printf("%6d %6d\n", v[0], v[1]);

		}
	}
	
	return 0;
}
