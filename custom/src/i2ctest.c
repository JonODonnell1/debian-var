#include <linux/i2c-dev.h>
#include <linux/i2c.h>
#include <stdint.h>
#include <stdio.h>
#include <sys/ioctl.h>
#include <fcntl.h>
#include <string.h>
#include <stdlib.h>
#include <unistd.h>

int i2c_init(const char *i2c_fname)
{
    int i2c_fd = open(i2c_fname, O_RDWR);
    if (i2c_fd < 0) {
        fprintf(stderr,
                "i2c_init: open('%s') = %d\n",
                i2c_fname,
                i2c_fd);
        return -1;
    }

    return i2c_fd;
}

void i2c_close(int i2c_fd)
{
    if (i2c_fd > 0) close(i2c_fd);
}

int i2c_write(int i2c_fd, uint8_t slave_addr, uint8_t reg, uint8_t n, uint8_t *data, uint8_t nRetries)
{
    uint8_t outbuf[256];
    struct i2c_msg msgs[1];
    struct i2c_rdwr_ioctl_data msgset;

    outbuf[0] = reg;
    if (n) memcpy(&outbuf[1], data, n);

    msgs[0].addr = slave_addr;
    msgs[0].flags = 0;
    msgs[0].len = n+1;
    msgs[0].buf = outbuf;

    msgset.msgs = msgs;
    msgset.nmsgs = 1;

    for (int i=0; i<nRetries; i++) {
    int result = ioctl(i2c_fd,
                       I2C_RDWR,
                       &msgset);
        if (result < 0 && i == nRetries-1) {
            fprintf(stderr,
                    "i2c_write: ioctl(I2C_RDWR) = %d\n",
                    result);
            return -1;
        }
        if (result > 0) break;
        usleep(500);
    }

    return 0;
}

int i2c_read(int i2c_fd, uint8_t slave_addr, uint8_t reg, uint8_t n, uint8_t *data)
{
    uint8_t outbuf[1];
    struct i2c_msg msgs_wr[1];
    struct i2c_rdwr_ioctl_data msgset_wr;
    struct i2c_msg msgs_rd[1];
    struct i2c_rdwr_ioctl_data msgset_rd;
    const int nRetries = 10;

    outbuf[0] = reg;
    memset(data, 0, n);

    msgs_wr[0].addr = slave_addr;
    msgs_wr[0].flags = I2C_M_STOP;     // set STOP at end of write
    msgs_wr[0].len = 1;
    msgs_wr[0].buf = outbuf;

    msgset_wr.msgs = msgs_wr;
    msgset_wr.nmsgs = 1;

    msgs_rd[0].addr = slave_addr;
    msgs_rd[0].flags = I2C_M_RD;       // send START again (no | I2C_M_NOSTART)
    msgs_rd[0].len = n;
    msgs_rd[0].buf = data;

    msgset_rd.msgs = msgs_rd;
    msgset_rd.nmsgs = 1;
    
    for (int i=0; i<nRetries; i++) {
        int result = ioctl(i2c_fd,
                           I2C_RDWR,
                           &msgset_wr);
        if (result < 0 && i == nRetries-1) {
            fprintf(stderr,
                    "i2c_read: ioctl(I2C_RDWR, msgset_wr) = %d\n",
                    result);
            return -1;
        }
        if (result > 0) break;
        usleep(500);
    }

    for (int i=0; i<nRetries; i++) {
        int result = ioctl(i2c_fd,
                           I2C_RDWR,
                           &msgset_rd);
        if (result < 0 && i == nRetries-1) {
            fprintf(stderr,
                    "i2c_read: ioctl(I2C_RDWR, msgset_rd) = %d\n",
                    result);
            return -1;
        }
        if (result > 0) break;
        usleep(500);
    }

    return n;
}

void Usage()
{
    fprintf(stderr,
            "i2ctest -- Test i2c device read\n"
            "Usage: i2ctest BUS ADDRESS REG N\n"
            "  BUS  -- i2c bus number\n"
            "          (1-10)\n"
            "  ADDR -- i2c address of device\n"
            "          (1-127 or 0x01-0x7F)\n"
            "  REG  -- First register number on device to write (optional)\n"
            "          (0-255 or 0x00-0xFF)\n"
            "  N    -- Number of registers to read\n"
            "          (0-255 or 0x00-0xFF)\n");
}


int main(int argc, char **argv)
{
    int file;
    char *pEnd;
    int i2c_bus = 1;
    uint8_t i2c_address = 0x10;
    uint8_t i2c_reg = 0;
    uint8_t i2c_n = 4;
    uint8_t buffer[255];
    char filename[20];
    int result;
    
    if (argc != 5) {
        Usage();
        return 1;
    }

    i2c_bus = (int)strtol(argv[1], &pEnd, 0);
    if (pEnd == argv[1] || *pEnd > ' ') {
        fprintf(stderr, "i2ctest: Error parsing i2c bus number.\nArg: %s\n", argv[1]);
        return 1;
    }

    i2c_address = (int)strtol(argv[2], &pEnd, 0);
    if (pEnd == argv[2] || *pEnd > ' ') {
        fprintf(stderr, "i2ctest: Error parsing i2c device address.\nArg: %s\n", argv[2]);
        return 1;
    }

    i2c_reg = (char)strtol(argv[3], &pEnd, 0);
    if (pEnd == argv[3] || *pEnd > ' ') {
        fprintf(stderr, "i2ctest: Error parsing i2c register number.\nArg: %s\n", argv[3]);
        i2c_close(file);
        return 1;
    }

    i2c_n = (char)strtol(argv[4], &pEnd, 0);
    if (pEnd == argv[4] || *pEnd > ' ') {
        fprintf(stderr, "i2cprog: Error parsing i2c register count.\nArg: %s\n", argv[4]);
        i2c_close(file);
        return 1;
     }

    snprintf(filename, 19, "/dev/i2c-%d", i2c_bus);
    file = i2c_init(filename);
    if (file < 0) {
        return 1;
    }

    result = i2c_read(file,
                      i2c_address,
                      i2c_reg,
                      i2c_n,
                       buffer);
    if (result > 0) {
        for (int i=0; i<i2c_n; i++)
            printf("0x%02X: 0x%02X\n",
                   i2c_reg+i,
                   buffer[i]);
    }

    i2c_close(file);

    return 0;
}
