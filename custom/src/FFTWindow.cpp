#include <math.h>
#include <stdlib.h>

typedef float FLOAT;

#include "FFTWindow.h"

static FLOAT getexpval(long index,long Length,FLOAT ExpRatio)
{
	FLOAT scale = (FLOAT)(log(0.5)/(ExpRatio > 1e-20f ? ExpRatio : 1e-30f));
	return (FLOAT)exp(((FLOAT)index/(FLOAT)Length)*scale);
}


void FFTWindow(FLOAT *x,
               long N,
               FFTWindowType WinType,
               int direction,
               FLOAT ExpRatio,
               FLOAT ForceConst)
{
	const FLOAT pi = 3.1415926535897932384626433832795L;
	const long Mid = N / 2L;
	const FLOAT delta = 2.0 * pi / (N - 1L);

	long ForceIndex=0L;

	long i;

	for (i=0L; i<N; i++)
	{
		FLOAT xx;
		FLOAT ang = (i-Mid) * delta;
		switch (WinType)
		{
			default: 
			case UNIFORM_WINDOW:           // none
				xx = 1.0;
				break;

			case HANNING_WINDOW:           // hanning
				xx = 1.0 + cos(ang);
				break;

			case HAMMING_WINDOW:           // hamming
				xx = 1.0 + 0.857504*cos(ang);
				break;

			case BLACKMAN_WINDOW:           // blackman
				xx = 1.0 +
				     1.171912*cos(ang) +
				     0.184449*cos(2.0*ang);
				break;
			
			case FLATTOP_WINDOW:           // flat-top
				xx = 0.9994484 + 
				     1.911456*cos(ang) +
				     1.078578*cos(2.0*ang) +
				     0.183162*cos(3.0*ang);
				break;
			
			case P210_WINDOW:           // P210
				xx = 1.0 +
				     1.22258*cos(ang) +
				     0.22258*cos(2.0*ang);
				break;
			
			case TRIANGLE_WINDOW:
				xx = 4.0/(1.0-fabs((FLOAT)i-Mid)/Mid);
				break;
			
			case EXPONENTIAL_WINDOW:
				xx = getexpval(i,N,ExpRatio);
				break;
			
			case FORCE_WINDOW:
				if(i<N*ForceConst || direction<0)
				{
					xx = 1.0f; /* starts uniform */
				}
				else
				{
					if(i>=N*ForceConst*3.0/2.0)
					{
						xx = 0.f; /* ends at 0 */
					}
					else
					{
						// transitions with a sine wave
						FLOAT pi_div_len = pi/(FLOAT)(N*ForceConst/2.0);
						xx = 0.5f + (0.5f*cos(pi_div_len*ForceIndex)); /* transitions with a sine */
						ForceIndex++;
					}
				}
				xx *= getexpval(i,N,ExpRatio); // multiply by the exponential window
				break;
		}

		if (direction > 0)
		{
			x[i] *= xx;
		}
		else
		{
			if (xx == 0.0)
				x[i] = 0;
			else
				x[i] = x[i] / xx;
		}
	}
}

