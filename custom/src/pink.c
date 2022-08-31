#include <time.h>
#include "pink.h"


/************************************************************/
/* Calculate pseudo-random 32 bit number based on linear congruential method. */
static unsigned long GenerateRandomNumber( void )
{
	static int first = 1;
	static unsigned long randSeed;
	if (first)
	{
		randSeed = time(NULL);  /* Change this for different random sequences. */
		first = 0;
	}

	randSeed = (randSeed * 196314165) + 907633515;
	return randSeed;
}

/* Setup PinkNoise structure for N rows of generators. */
void PinkNoiseInitialize( PinkNoise *pink )
{
	int i;
	long pmax;
	pink->pink_Index = 0;
	pink->pink_IndexMask = (1<<PINK_ROWS) - 1;
/* Calculate maximum possible signed random value. Extra 1 for white noise always added. */
#if !PINK_HIPASS
	pink->pMax = (PINK_ROWS + 1) * (1<<(PINK_RANDOM_BITS-1));
#else
	pink->pMax = (PINK_ROWS + 1) * (1<<((PINK_RANDOM_BITS+PINK_HIPASS_CORRECTION_BITS)-1));
#endif
/* Initialize rows. */
	for( i=0; i<PINK_ROWS; i++ ) pink->pink_Rows[i] = 0;
	pink->pink_RunningSum = 0;
#ifdef PINK_MEASURE
	pink->pinkMinInt = 0x7FFFFFFF;
	pink->pinkMaxInt = 0x80000000;
#endif
#if PINK_HIPASS
	for (i=0; i<PINK_HIPASS; i++)
		pink->pAvgData[i] = 0;
	pink->pAvg = 0;
	pink->iAvg = 0;
	
	for (i=0; i<PINK_HIPASS; i++)
		PinkNoiseGenerate(pink);
#endif
}

int PinkNoiseGenerate( PinkNoise *pink )
{
	long newRandom;
	long sum;

/* Increment and mask index. */
	pink->pink_Index = (pink->pink_Index + 1) & pink->pink_IndexMask;

/* If index is zero, don't update any random values. */
	if( pink->pink_Index != 0 )
	{
	/* Determine how many trailing zeros in PinkIndex. */
	/* This algorithm will hang if n==0 so test first. */
		int numZeros = 0;
		int n = pink->pink_Index;
		while( (n & 1) == 0 )
		{
			n = n >> 1;
			numZeros++;
		}

	/* Replace the indexed ROWS random value.
	 * Subtract and add back to RunningSum instead of adding all the random
	 * values together. Only one changes each time.
	 */
		pink->pink_RunningSum -= pink->pink_Rows[numZeros];
		newRandom = ((long)GenerateRandomNumber()) >> PINK_RANDOM_SHIFT;
		pink->pink_RunningSum += newRandom;
		pink->pink_Rows[numZeros] = newRandom;
	}
	
/* Add extra white noise value. */
	newRandom = ((long)GenerateRandomNumber()) >> PINK_RANDOM_SHIFT;
	sum = pink->pink_RunningSum + newRandom;
	
#if PINK_HIPASS
	pink->pAvg += (sum - pink->pAvgData[pink->iAvg]);
	pink->pAvgData[pink->iAvg] = sum;
	sum = pink->pAvgData[(pink->iAvg+PINK_HIPASS/2) % PINK_HIPASS] - pink->pAvg/PINK_HIPASS;
	pink->iAvg = (pink->iAvg+1)%PINK_HIPASS;
	sum = PINK_HIPASS_CORRECTION_NUMERATOR*sum/PINK_HIPASS_CORRECTION_DENOMINATOR;
#endif
	

#ifdef PINK_MEASURE
	if (sum > pink->pinkMaxInt) pink->pinkMaxInt = sum;
	if (sum < pink->pinkMinInt) pink->pinkMinInt = sum;
#endif

	if (sum > 32767) sum = 32767;
	if (sum < -32768) sum = -32768;

	return (int)sum;
}
