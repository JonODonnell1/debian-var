#include <stdlib.h>
#include <stdio.h>
#include <getopt.h>
#include <string.h>
#include <errno.h>

#define MAX_PATTERN 100
#define MAX_FILES   26
#define MAX_BUFF 1024

int main(int argc, char **argv)
{
	int opt;
	static char sPattern[MAX_PATTERN+1] = "";
	int bVerbose = 0;
    int nBytes = 1;
    static FILE *fFiles[MAX_FILES];
    static long nRead[MAX_FILES] = { 0 };
    long nPad = 0;
    static struct {
        int nBytes; //
        int iFile; // File index (<0 indicates padding)
    } Pattern[100];
    int nPatterns = 0;
    int nFiles;
    int iPattern;
    int iFile;
    int bDone = 0;
    static unsigned char Buffer[MAX_BUFF];
	
	while ((opt = getopt(argc, argv, "vhp:n:")) != -1)
	{
		switch (opt)
		{
			case 'v':
				bVerbose = 1;
				break;
            case 'n':
                nBytes = atoi(optarg);
                break;
			case 'p':
                strncpy(sPattern, optarg, MAX_PATTERN);
				break;
			case '?':
				fprintf(stderr, "Option '%c' unrecognized\n\n", optopt);
			case ':':
                if (opt==':')
    				fprintf(stderr, "Option '%c' requires value\n\n", optopt);
			case 'h':
			default:
				printf("interleave [-h] [-p ""PATTERN""] [-v] fileA [fileB [fileC [fileD [...]]]]\n"
				       "  -h                Print usage\n"
				       "  -v                Verbose\n"
				       "  -n count          Specify the default number of bytes to take from each file\n"
				       "                      before proceeding to the next file (default: 1)\n"
				       "  -p ""PATTERN""    Specify interleave pattern\n"
				       "                      PATTERN consists of a 1 or more sets of a number followed by \n"
				       "                        an optional letter.\n"
                       "                      A number by itself indicates the number of 0x00 padding bytes\n"
                       "                      A number followed by a letter indicates the number of bytes\n"
                       "                        to be taken from the speficied file (1024 max)\n"
                       "                      A negative number followed by a letter indicates the number\n"
                       "                        byte-reversed bytes to be taken from the specified file\n"
                       "                      The default is n bytes from each file in order\n"
                       "                        where n is speficified by the -n argument\n"
				       "n");
				       
				printf("Example:\n"
				       "  interleave a.bin b.bin c.bin\n"
                       "    Output\n"
                       "       1 byte from a.bin\n"
                       "       1 byte from b.bin\n"
                       "       1 byte from c.bin\n"
                       "       repeating until the end of any file\n"
				       "  interleave -n 4 a.bin b.bin\n"
                       "    Output\n"
                       "       4 bytes from a.bin\n"
                       "       4 bytes from b.bin\n"
                       "       repeating until the end of any file\n"
                       "  interleave -p ""4c 1 2a 1b"" a.bin b.bin c.bin\n"
                       "    Output:\n"
                       "       4 bytes from a.bin\n"
                       "       1 pad byte (0x00)\n"
                       "       2 bytes from a.bin\n"
                       "       1 byte from b.bin\n"
                       "       repeating until the end of any file\n"
                       );
				return 1;
		}
	}

    nFiles = argc-optind;
    if (nFiles==0) {
        fprintf(stderr, "At least 1 file must be speficied\n");
        return 1;
    }

    if (sPattern[0]==0) {
        // no pattern specified
        for (iPattern=0; iPattern<nFiles; iPattern++) {
            Pattern[iPattern].iFile = iPattern;
            Pattern[iPattern].nBytes = nBytes;
        }
        nPatterns = nFiles;
    } else {
        // parse pattern
        const char *p = sPattern;
        nPatterns = 0;
        while (*p==' ' || *p=='\t') p++;
        while (*p) {
            char *pEnd;
            Pattern[nPatterns].nBytes = strtol(p, &pEnd, 10);
            if (Pattern[nPatterns].nBytes == 0) {
                fprintf(stderr, "Error parsing pattern. \n");
 //               fprintf(stderr, "  p=""%s""\n", p);
 //               if (pEnd) {
 //                   fprintf(stderr, "  pEnd=""%s""\n", pEnd);
 //               } else {
 //                   fprintf(stderr, "  pEnd=NULL\n");
 //              }
                return 1;
            }
            if (Pattern[nPatterns].nBytes > MAX_BUFF || Pattern[nPatterns].nBytes < -MAX_BUFF || Pattern[nPatterns].nBytes==-1) {
                fprintf(stderr, "Invalid byte count: %d\nMust be -%d to -2 or 1 to %d\n", Pattern[nPatterns].nBytes, MAX_BUFF, MAX_BUFF);
                return 1;
            }
            p = pEnd;
            if (*p>='a' && *p<='z') {
                Pattern[nPatterns].iFile = *p-'a';
                if (Pattern[nPatterns].iFile >= nFiles) {
                    fprintf(stderr, "File letter more than files speficied. \n");
                    return 1;
                }
                p++;
            } else if (*p>='A' && *p<='Z') {
                Pattern[nPatterns].iFile = *p-'A';
                if (Pattern[nPatterns].iFile >= nFiles) {
                    fprintf(stderr, "File letter more than files speficied. \n");
                    return 1;
                }
                p++;
            } else if (*p==' ' || *p=='\t' || *p==0) {
                Pattern[nPatterns].iFile = -1;
            }
            nPatterns++;
            while (*p==' ' || *p=='\t') p++;
        }
    }

    if (bVerbose) {
        for (iFile=0; iFile<nFiles; iFile++) {
            fprintf(stderr, "File %c: %s\n", 'A'+iFile, argv[optind+iFile]);
        }
        fprintf(stderr, "Pattern:\n");
        for (iPattern=0; iPattern<nPatterns; iPattern++) {
            if (Pattern[iPattern].iFile < 0) {
                fprintf(stderr, "   %4d bytes: 0x00 (padding)\n", Pattern[iPattern].nBytes);
            } else if (Pattern[iPattern].nBytes > 0) {
                fprintf(stderr, "   %4d bytes: File %c\n", Pattern[iPattern].nBytes, Pattern[iPattern].iFile+'A');
            } else {
                fprintf(stderr, "   %4d bytes: File %c (byte-reversed)\n", -Pattern[iPattern].nBytes, Pattern[iPattern].iFile+'A');
            }
        }
    }

    for (iFile=0; iFile<nFiles; iFile++) {
        fFiles[iFile] = fopen(argv[optind+iFile], "r");
        if (fFiles[iFile]==NULL) {
            for (int i=0; i<iFile; i++) {
                fclose(fFiles[i]);
            }
        }
    }

    while (!bDone) {
        for (iPattern=0; iPattern<nPatterns && !bDone; iPattern++) {
            int n = Pattern[iPattern].nBytes;
            int nr;
            if (Pattern[iPattern].iFile >= 0) {
                if (nr=fread(Buffer, 1, abs(n), fFiles[Pattern[iPattern].iFile]) == abs(n)) {
                    if (n > 0) {
                        fwrite(Buffer, 1, n, stdout);
                    } else {
                        for (int i=abs(n)-1; i>=0; i--) {
                            fwrite(&Buffer[i], 1, 1, stdout);
                        }
                    }
                    nRead[Pattern[iPattern].iFile] += abs(n);
                } else {
                    if (bVerbose) {
                        fprintf(stderr, "EOF %s\n", argv[optind+Pattern[iPattern].iFile]);
                    }
                    bDone = 1;
                }
            } else {
                for (int i=0; i<abs(n); i++) {
                    fputc(0x00, stdout);
                }
                nPad += abs(n);
            }
        }
    }

    if (bVerbose) {
        long nTotal = 0;
        for (iFile=0; iFile<nFiles; iFile++) {
            fprintf(stderr, "File %s, Bytes: %ld\n", argv[optind+iFile], nRead[iFile]);
            nTotal+= nRead[iFile];
        }
        fprintf(stderr, "Padding Bytes: %ld\n", nPad);
        nTotal += nPad;
        fprintf(stderr, "Total Bytes: %ld\n", nTotal);
    }

    for (iFile=0; iFile<nFiles; iFile++) {
        fclose(fFiles[iFile]);
    }

    return 0;
}