/*
	Copyright 2018 Legrand North America
	Author: Jon O'Donnell
*/

#include <linux/i2c-dev.h>
#include <stdio.h>
#include <sys/ioctl.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <string.h>
#include <stdlib.h>
#include <unistd.h>

#define MAX_BURST 100

int i2c_write(int i2c_file, char reg, char *buff, int nBuff)
{
    char tBuff[MAX_BURST+1];
    int res;

    if (nBuff==0 || nBuff > MAX_BURST) return -1;
    tBuff[0] = reg;
    memcpy(&tBuff[1], buff, nBuff);
    res = write(i2c_file, tBuff, nBuff+1);
    if (res > 0)
        res = res-1;
    return res;
}

void Usage()
{
    fprintf(stderr,
            "i2cprog -- write data to i2c device\n"
            "Usage: i2cprog BUS ADDRESS [REG VAL ...]\n"
            "  BUS  -- i2c bus number\n"
            "          (1-10)\n"
            "  ADDR -- i2c address of device\n"
            "          (1-127 or 0x01-0x7F)\n"
            "  REG  -- First register number on device to write (optional)\n"
            "          (0-255 or 0x00-0xFF)\n"
            "  VAL  -- One or more values to write to consecutive registers (optional)\n"
            "          (0-255 or 0x00-0xFF)\n"
            "   If REG and VAL are not specified on the command line, sets of registers and\n"
            "    values will be read from STDIN.  The first number on each line is the\n"
            "    starting register.  Each additional number on the line are values to be\n"
            "    written starting at the specified register.\n"
            "   Example:\n"
            "     0x00 0x00\n"
            "     0x3D 0x1A 0x1F\n");
}

void skipwhitespace(char **pp)
{
    char *p = *pp;
    char c;

    while ((c = *p) != 0) {
        if (c > ' ')
            break;
        p++;
    }

    *pp = p;
}


int main(int argc, char **argv)
{
    int file;
    int i2c_bus;
    int i2c_address;
    char filename[20];
    int res;
    char buff[MAX_BURST];
    int nBuff;
    char reg;
    int iBuff;
    char *pEnd;
    int ret = 0;

    if (argc < 3 || argc == 5) {
        Usage();
        return 1;
    }

    i2c_bus = (int)strtol(argv[1], &pEnd, 0);
    if (pEnd == argv[1] || *pEnd > ' ') {
        fprintf(stderr, "i2cprog: Error parsing i2c bus number.\nArg: %s\n", argv[1]);
        return 1;
    }
    i2c_address = (int)strtol(argv[2], &pEnd, 0);
    if (pEnd == argv[2] || *pEnd > ' ') {
        fprintf(stderr, "i2cprog: Error parsing i2c device address.\nArg: %s\n", argv[2]);
        return 1;
    }

    snprintf(filename, 19, "/dev/i2c-%d", i2c_bus);
    file = open(filename, O_RDWR);
    if (file < 0) {
        fprintf(stderr, "i2cprog: Error opening i2c device %s\n", filename);
        return 1;
    }
    if ((res = ioctl(file, I2C_SLAVE_FORCE, i2c_address)) < 0) {
        fprintf(stderr, "i2cprog: Error opening i2c slave 0x%02X (res=%d)\n", i2c_address, res);
        ret = 1;
        goto _end;
    }

    if (argc > 3) {
        // from command line
        reg = (char)strtol(argv[3], &pEnd, 0);
        if (pEnd == argv[3] || *pEnd > ' ') {
            fprintf(stderr, "i2cprog: Error parsing i2c register number.\nArg: %s\n", argv[3]);
            ret = 1;
            goto _end;
        }
        nBuff = argc - 4;
        for (iBuff = 0; iBuff < nBuff; iBuff++) {
            buff[iBuff] = (char)strtol(argv[4+iBuff], &pEnd, 0);
            if (pEnd == argv[4+iBuff] || *pEnd > ' ') {
                fprintf(stderr, "i2cprog: Error parsing value.\nArg: %s\n", argv[4+iBuff]);
                ret = 1;
                goto _end;
            }
        }
        if ((res = i2c_write(file, reg, buff, nBuff)) != nBuff) {
            fprintf(stderr, "i2cprog: Error writing 0x%02X:0x%02X (res=%d)\n", buff[0], buff[1], res);
            ret = 1;
            goto _end;
        }
    } else {
        // from stdin
        char line[1024];
        while (fgets(line, 1024, stdin) != NULL) {
            char *p = line;
            skipwhitespace(&p);
            if (*p == 0 || *p == '#')
                continue;

            reg = strtol(p, &pEnd, 0);
            if (p == pEnd || (*pEnd > ' ' && *pEnd != '#')) {
                fprintf(stderr, "i2cprog: error reading register.\nLine:\n%s\n", line);
                goto _end;
            }
            p = pEnd;
            skipwhitespace(&p);
            if (*p == 0 || *p == '#') {
                fprintf(stderr, "i2cprog: error no values found on line.\nLine:\n%s\n",line);
                ret = 1;
                goto _end;
            }
            nBuff = 0;
            while (*p != 0 && *p != '#') {
                buff[nBuff++] = strtol(p, &pEnd, 0);
                if (p == pEnd || (*pEnd > ' ' && *pEnd != '#')) {
                    fprintf(stderr, "i2cprog: error reading value.\nLine:\n%s\n",line);
                    ret = 1;
                    goto _end;
                }
                p = pEnd;
                skipwhitespace(&p);
            }
            if ((res = i2c_write(file, reg, buff, nBuff)) != nBuff) {
                fprintf(stderr, "i2cprog: Error writing 0x%02X:0x%02X (res=%d)\nLine:\n%s\n", buff[0], buff[1], res, line);
                ret = 1;
                goto _end;
            }
        }
    }
_end:
    close(file);
    return ret;
}
