#ifndef __FFTWindow_h__
#define __FFTWindow_h__

typedef enum
	{
		UNIFORM_WINDOW,
		HANNING_WINDOW,
		HAMMING_WINDOW,
		BLACKMAN_WINDOW,
		FLATTOP_WINDOW,
		P210_WINDOW,
		TRIANGLE_WINDOW,
		EXPONENTIAL_WINDOW,
		FORCE_WINDOW
	} FFTWindowType;

void FFTWindow(FLOAT *x,
               long N,
               FFTWindowType WinType,
               int direction = 1,
               FLOAT ExpRatio = 1.0f,
               FLOAT ForceConst = 0.0f);

#endif
