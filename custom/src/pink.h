#ifndef __PINK_H__
#define __PINK_H__

#define PINK_MEASURE

#define PINK_HIPASS                        (48000/20)
#define PINK_HIPASS_CORRECTION_NUMERATOR   (4)   // corrections experimentally determined
#define PINK_HIPASS_CORRECTION_DENOMINATOR (5)
#define PINK_HIPASS_CORRECTION_BITS        (1)

#define PINK_ROWS                          (15)  // 15 & 12 will create numbers between -32768 & 32767
#define PINK_RANDOM_BITS                   (12)


#define PINK_MAX_RANDOM_ROWS               (30)
#if !PINK_HIPASS
#define PINK_RANDOM_SHIFT                  ((sizeof(long)*8)-PINK_RANDOM_BITS)
#else
#define PINK_RANDOM_SHIFT                  ((sizeof(long)*8)-(PINK_RANDOM_BITS+PINK_HIPASS_CORRECTION_BITS))
#endif

typedef struct
{
        long      pink_Rows[PINK_MAX_RANDOM_ROWS];
        long      pink_RunningSum;   /* Used to optimize summing of generators. */
        int       pink_Index;        /* Incremented each sample. */
        int       pink_IndexMask;    /* Index wrapped by ANDing with this mask. */
        long      pMax;
#if PINK_HIPASS
        int       pAvgData[PINK_HIPASS];
        long      pAvg;
        int       iAvg;
#endif
#ifdef PINK_MEASURE
        long      pinkMaxInt;
        long      pinkMinInt;
#endif
} PinkNoise;

void PinkNoiseInitialize( PinkNoise *pink );
int PinkNoiseGenerate( PinkNoise *pink );

#endif
