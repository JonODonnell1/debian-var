#!/bin/python3
from periphery import I2C
from typing import List, Tuple, Dict
import json

REG_FIELD={
    "bits": [ 0 ],       # low to high
    "value": 0,
    "default": 0,
    "choices": [ "OFF", "ON" ]
}
REG={
    "registers": [ 0 ],  # low to high
    "value": 0,           # binary value
    "fields": {
        "field_name": REG_FIELD
    }
}

src4392_page0 = (
    {   "name": "0x01",
        "regs": [ 0x01 ],
        "desc": "Power-Down and Reset",
        "fields": {
            "PDNSRCn": {
                "bits": [ 0 ],
                "default": 0,
                "choices": [ "Enabled", "Disabled" ],
                "desc": "Power-Down for the SRC Function Block"
            },
            "PDNRXn": {
                "bits": [ 1 ],
                "default": 0,
                "choices": [ "Enabled", "Disabled" ],
                "desc": "Power-Down for the Receiver Function Block"
            },
            "PDNTXn": {
                "bits": [ 2 ],
                "default": 0,
                "choices": [ "Enabled", "Disabled" ],
                "desc": "Power-Down for the Transmitter Function Block"
            },
            "PDNPBn": {
                "bits": [ 3 ],
                "default": 0,
                "choices": [ "Enabled", "Disabled" ],
                "desc": "Power-Down for Serial Port B"
            },
            "PDNPAn": {
                "bits": [ 4 ],
                "default": 0,
                "choices": [ "Enabled", "Disabled" ],
                "desc": "Power-Down for Serial Port A"
            },
            "PDNALLn": {
                "bits": [ 5 ],
                "default": 0,
                "choices": [ "Enabled", "Disabled" ],
                "desc": "Power-Down for All Functions"
            },
            "RESET": {
                "bits": [ 7 ],
                "default": 0,
                "choices": [ "Disabled", "Enabled" ],
                "desc": "Software Reset"
            }
        }
    },
    {   "name": "0x02",
        "regs": [ 0x02 ],
        "desc": "Global Interrupt Status",
        "fields": {
            "SRC": {
                "bits": [ 0 ],
                "default": 0,
                "desc": "SRC Function Block Interrupt Status (Active High)"
            },
            "RX": {
                "bits": [ 1 ],
                "default": 0,
                "desc": "Receiver Function Block Interrupt Status (Active High)"
            },
            "TX": {
                "bits": [ 2 ],
                "default": 0,
                "desc": "Transmitter Function Block Interrupt Status (Active High)"
            },
        }
    },
    {   "name": "0x03",
        "regs": [ 0x03 ],
        "desc": "Port A Control",
        "fields": {
            "AFMT": {
                "bits": [ 0, 1, 2 ],
                "default": 0,
                "choices": [ "24-Bit Left-Justified", "24-Bit Phillips I2S", "Unused", "Unused", "16-Bit Right-Justified", "18-Bit Right-Justified", "20-Bit Right-Justified", "24-Bit Right-Justified" ],
                "desc": "Port A Audio Data Format"
            },
            "AM/S": {
                "bits": [ 3 ],
                "default": 0,
                "choices": [ "Slave mode", "Master mode" ],
                "desc": "Port A Slave/Master Mode"
            },
            "AOUTS": {
                "bits": [ 4, 5 ],
                "default": 0,
                "choices": [ "Port A Input", "Port B Input", "DIR", "SRC" ],
                "desc": "Port A Output Data Source"
            },
            "AMUTE": {
                "bits": [ 6 ],
                "default": 0,
                "choices": [ "Unmuted", "Muted" ],
                "desc": "Port A Output Mute"
            },
        }
    },
    {   "name": "0x04",
        "regs": [ 0x04 ],
        "desc": "Port A Control",
        "fields": {
            "ADIV": {
                "bits": [ 0, 1 ],
                "default": 0,
                "choices": [ "Divide by 128", "Divide by 256", "Divide by 384", "Divide by 512" ],
                "desc": "Port A Master Clock Divider"
            },
            "ACLK": {
                "bits": [ 2, 3 ],
                "default": 0,
                "choices": [ "MCLK", "RXCKI", "RXCKO", "Reserved" ],
                "desc": "Port A Master Clock Source"
            },
        }
    },
    {   "name": "0x05",
        "regs": [ 0x05 ],
        "desc": "Port B Control",
        "fields": {
            "BFMT": {
                "bits": [ 0, 1, 2 ],
                "default": 0,
                "choices": [ "24-Bit Left-Justified", "24-Bit Phillips I2S", "Unused", "Unused", "16-Bit Right-Justified", "18-Bit Right-Justified", "20-Bit Right-Justified", "24-Bit Right-Justified" ],
                "desc": "Port B Audio Data Format"
            },
            "BM/S": {
                "bits": [ 3 ],
                "default": 0,
                "choices": [ "Slave", "Master" ],
                "desc": "Port B Slave/Master Mode"
            },
            "BOUTS": {
                "bits": [ 4, 5 ],
                "default": 0,
                "choices": [ "Port B Input", "Part A Input", "DIR", "SRC" ],
                "desc": "Port B Output Source"
            },
            "BMUTE": {
                "bits": [ 6 ],
                "default": 0,
                "choices": [ "Unmuted", "Muted" ],
                "desc": "Port B Output Mute"
            },
        }
    },
    {   "name": "0x06",
        "regs": [ 0x06 ],
        "desc": "Port B Control",
        "fields": {
            "BDIV": {
                "bits": [ 0, 1 ],
                "default": 0,
                "choices": [ "Divide by 128", "Divide by 256", "Divide by 384", "Divide by 512" ],
                "desc": "Port B Master Clock Divider"
            },
            "BCLK": {
                "bits": [ 2, 3 ],
                "default": 0,
                "choices": [ "MCLK", "RXCKI", "RXCKO", "Reserved" ],
                "desc": "Port B Master Clock Source"
            },
        }
    },
    {   "name": "0x07",
        "regs": [ 0x07 ],
        "desc": "Transmitter Control",
        "fields": {
            "BSSL": {
                "bits": [ 0 ],
                "default": 0,
                "choices": [ "Data Slip Condition", "Block Start Condition" ],
                "desc": "Block Start or Asynchronous Data Slip Interrupt Trigger Selection"
            },
            "VALID": {
                "bits": [ 1 ],
                "default": 0,
                "choices": [ "Valid", "Invalid" ],
                "desc": "Validity (V) Data Bit"
            },
            "BLSM": {
                "bits": [ 2 ],
                "default": 0,
                "choices": [ "Input", "Output" ],
                "desc": "Transmitter Block Start Input/Output Mode"
            },
            "TXIS": {
                "bits": [ 3, 4 ],
                "default": 0,
                "choices": [ "Port A", "Port B", "DIR", "SRC" ],
                "desc": "Transmitter Input Data Source"
            },
            "TXDIV": {
                "bits": [ 5, 6 ],
                "default": 0,
                "choices": [ "Divide by 128", "Divide by 256", "Divide by 384", "Divide by 512" ],
                "desc": "Transmitter Master Clock Divider"
            },
            "TXCLK": {
                "bits": [ 7 ],
                "default": 0,
                "choices": [ "MCLK Input", "RXCKO" ],
                "desc": "Transmitter Master Clock Source"
            },
        }
    },
    {   "name": "0x08",
        "regs": [ 0x08 ],
        "desc": "Transmitter Control",
        "fields": {
            "TXOFF": {
                "bits": [ 0 ],
                "default": 0,
                "choices": [ "Enabled", "Disabled" ],
                "desc": "Transmitter Line Driver Output Enable"
            },
            "TXMUTE": {
                "bits": [ 1 ],
                "default": 0,
                "choices": [ "Unmuted", "Muted" ],
                "desc": "Transmitter Audio Data Mute"
            },
            "AESOFF": {
                "bits": [ 2 ],
                "default": 0,
                "choices": [ "AES On", "AES Off" ],
                "desc": "AESOUT Output Enable"
            },
            "TXBTD": {
                "bits": [ 3 ],
                "default": 0,
                "choices": [ "Enabled", "Disabled" ],
                "desc": "Transmitter C and U Data Buffer Transfer Disable"
            },
            "LDMUX": {
                "bits": [ 4 ],
                "default": 0,
                "choices": [ "DIT AES3 Encoder Output", "Bypass Multiplexer Output" ],
                "desc": "Transmitter Line Driver Input Source Selection"
            },
            "AESMUX": {
                "bits": [ 5 ],
                "default": 0,
                "choices": [ "DIT AES3 Encoder Output", "Bypass Multiplexer Output" ],
                "desc": "AESOUT CMOS Buffer Input Source Selection"
            },
            "BYPMUX": {
                "bits": [ 6, 7 ],
                "default": 0,
                "choices": [ "RX1", "RX2", "RX3", "RX4" ],
                "desc": "Bypass Multiplexer Source Selection"
            },
        }
    },
    {   "name": "0x09",
        "regs": [ 0x09 ],
        "desc": "Transmitter Control",
        "fields": {
            "TXCUS": {
                "bits": [ 0, 1 ],
                "default": 0,
                "choices": [ "Buffers not updated", "Updated via SPI or I2C", "Updated via DIR RA buffers", "first 10 bytes via SPI or I2C and remainder via DIR RA buffers" ],
                "desc": "Transmitter Channel Status and User Data Source"
            },
            "VALSEL": {
                "bits": [ 2 ],
                "default": 0,
                "choices": [ "VALID bit in control register 0x07", "bit is transferred from the DIR block with zero latency" ],
                "desc": "Transmitter Validity Bit Source"
            },
        }
    },
    {   "name": "0x0A",
        "regs": [ 0x0A ],
        "desc": "SRC and DIT Status",
        "fields": {
            "TBTI": {
                "bits": [ 0 ],
                "desc": "Transmitter Buffer Transfer Status, Active High"
            },
            "TSLIP": {
                "bits": [ 1 ],
                "default": 0,
                "desc": "Transmitter Source Data Slip Status, Active High"
            },
            "READY": {
                "bits": [ 4 ],
                "default": 0,
                "desc": "SRC Rate Estimator Ready Status, Active High"
            },
            "RATIO": {
                "bits": [ 5 ],
                "default": 0,
                "desc": "SRC Ratio Status, Active High"
            },
        }
    },
    {   "name": "0x0B",
        "regs": [ 0x0B ],
        "desc": "SRC and DIT Interrupt Mask",
        "fields": {
            "MTBTI": {
                "bits": [ 0 ],
                "default": 0,
                "choices": [ "BTI interrupt is masked", "BTI interrupt is enabled" ],
                "desc": "Transmitter Buffer Transfer Interrupt Mask"
            },
            "MTSLIP": {
                "bits": [ 1 ],
                "default": 0,
                "choices": [ "TSLIP interrupt is masked", "TSLIP interrupt is enabled" ],
                "desc": "Transmitter TSLIP Interrupt Mask"
            },
            "MREADY": {
                "bits": [ 4 ],
                "default": 0,
                "choices": [ "READY interrupt is masked", "READY interrupt is enabled" ],
                "desc": "SRC Ready Interrupt Mask"
            },
            "MRATIO": {
                "bits": [ 5 ],
                "default": 0,
                "choices": [ "RATIO interrupt is masked", "RATIO interrupt is enabled" ],
                "desc": "SRC Ratio Interrupt Mask"
            },
        }
    },
    {   "name": "0x0C",
        "regs": [ 0x0C ],
        "desc": "SRC and DIT Interrupt Mask",
        "fields": {
            "TBTIM": {
                "bits": [ 0, 1 ],
                "default": 0,
                "choices": [ "Rising Edge Active", "Falling Edge Active", "Level Active", "Reserved" ],
                "desc": "Transmitter Buffer Transfer Interrupt Mode"
            },
            "TSLIPM": {
                "bits": [ 2, 3 ],
                "default": 0,
                "choices": [ "Rising Edge Active", "Falling Edge Active", "Level Active", "Reserved" ],
                "desc": "Transmitter Data Source Slip Interrupt Mode"
            },
            "READYM": {
                "bits": [ 4, 5 ],
                "default": 0,
                "choices": [ "Rising Edge Active", "Falling Edge Active", "Level Active", "Reserved" ],
                "desc": "SRC Ready Interrupt Mode"
            },
            "RATIOM": {
                "bits": [ 6, 7 ],
                "default": 0,
                "choices": [ "Rising Edge Active", "Falling Edge Active", "Level Active", "Reserved" ],
                "desc": "SRC Ratio Interrupt Mode"
            },
        }
    },
    {   "name": "0x0D",
        "regs": [ 0x0D ],
        "desc": "Receiver Control",
        "fields": {
            "RXMUX": {
                "bits": [ 0, 1 ],
                "default": 0,
                "choices": [ "RX1", "RX2", "RX3", "RX4" ],
                "desc": "Receiver Input Source Selection"
            },
            "RXCLK": {
                "bits": [ 3 ],
                "default": 0,
                "choices": [ "RXCKI", "MCLK" ],
                "desc": "Receiver Reference Clock Source"
            },
            "RXBTD": {
                "bits": [ 4 ],
                "default": 0,
                "choices": [ "Enabled", "Disabled; the user may read C and U data from the DIR UA buffers" ],
                "desc": "Receiver C and U Data Buffer Transfer Disable"
            },
        }
    },
    {   "name": "0x0E",
        "regs": [ 0x0E ],
        "desc": "Receiver Control",
        "fields": {
            "RXCKOE": {
                "bits": [ 0 ],
                "default": 0,
                "choices": [ "Disabled; the RXCKO output is set to high-impedance", "Enabled; the recovered master clock is available at RXCKO" ],
                "desc": "RXCKOE Output Enable"
            },
            "RXCKOD": {
                "bits": [ 1, 2 ],
                "default": 0,
                "choices": [ "Passthrough", "PLL2 / 2", "PLL2 / 4", "PLL2 / 8" ],
                "desc": "RXCKO Output Clock Divider"
            },
            "RXAMLL": {
                "bits": [ 3 ],
                "default": 0,
                "choices": [ "Disabled", "Enabled; MUTE on LOL" ],
                "desc": "Receiver Automatic Mute for Loss of Lock"
            },
            "LOL": {
                "bits": [ 4 ],
                "default": 0,
                "choices": [ "PLL2 output clock is stopped for LOL", "PLL2 output clock free runs when LOL" ],
                "desc": "Receiver Loss of Lock Mode for the Recovered Clock (output from PLL2)"
            },
        }
    },
    {   "name": "0x0F-0x11",
        "regs": [ 0x0F, 0x10, 0x11 ],
        "desc": "Receiver PLL Configuration",
        "fields": {
            "D": {
                "bits": [ 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13 ],
                "default": 0,
                "desc": "Fractional part (0-9999) of K=J.D"
            },
            "J": {
                "bits": [ 14, 15, 16, 17, 18, 19 ],
                "default": 0,
                "desc": "Integer part (1 to 63) of K=J.D"
            },
            "P": {
                "bits": [ 20, 21, 22, 23 ],
                "default": 0,
                "desc": "Pre-Divider (1-7)"
            },
        }
    },
    {   "name": "0x12",
        "regs": [ 0x12 ],
        "desc": "Non-PCM Audio Detection",
        "fields": {
            "IEC61937": {
                "bits": [ 0 ],
                "default": 0,
                "choices": [ "Not an IEC61937 format", "IEC61937 format" ],
                "desc": "Indicates detection of an IEC 61937 data"
            },
            "DTS CD/LD": {
                "bits": [ 1 ],
                "default": 0,
                "choices": [ "CD/LD is not DTS encoded", "DTS CD/LD playback detected" ],
                "desc": "indicates detection of a DTS encoded audio"
            },
        }
    },
    {   "name": "0x13",
        "regs": [ 0x13 ],
        "desc": "Receiver Status",
        "fields": {
            "RXCKR": {
                "bits": [ 0, 1 ],
                "default": 0,
                "choices": [ "Clock rate not determined", "128fs", "256fs", "512fs" ],
                "desc": "Maximum Available Recovered Clock Rate"
            },
        }
    },
    {   "name": "0x14",
        "regs": [ 0x14 ],
        "desc": "Receiver Status",
        "fields": {
            "RBTI": {
                "bits": [ 0 ],
                "default": 0,
                "choices": [ "Buffer Transfer Incomplete, or No Buffer Transfer Interrupt Indicated", "Buffer Transfer Completed" ],
                "desc": "Receiver Buffer Transfer Interrupt Status"
            },
            "QCRC": {
                "bits": [ 1 ],
                "default": 0,
                "choices": [ "No Error", "Q-channel sub-code data CRC error detected" ],
                "desc": "Q-Channel Sub-Code CRC Status"
            },
            "UNLOCK": {
                "bits": [ 2 ],
                "default": 0,
                "choices": [ "No error; the DIR AES3 decoder and PLL2 are locked", "DIR lock error; the AES3 decoder and PLL2 are unlocked" ],
                "desc": "DIR Unlock Error Status"
            },
            "QCHG": {
                "bits": [ 3 ],
                "default": 0,
                "choices": [ "No change in Q-channel sub-code data", "Q-channel data has changed" ],
                "desc": "Q-Channel Sub-Code Data Change Status"
            },
            "BPERR": {
                "bits": [ 4 ],
                "default": 0,
                "choices": [ "No Error", "Bipolar Encoding Error Detected" ],
                "desc": "Bipolar Encoding Error Status"
            },
            "VBIT": {
                "bits": [ 5 ],
                "default": 0,
                "choices": [ "Valid Audio Data Indicated", "Non-Valid Data Indicated" ],
                "desc": "Validity Bit Status"
            },
            "PARITY": {
                "bits": [ 6 ],
                "default": 0,
                "choices": [ "No Error", "Parity Error Detected" ],
                "desc": "Parity Status"
            },
            "CSCRC": {
                "bits": [ 7 ],
                "default": 0,
                "choices": [ "No Error", "CRC Error Detected" ],
                "desc": "Channel Status CRC Status"
            },
        }
    },
    {   "name": "0x15",
        "regs": [ 0x15 ],
        "desc": "Receiver Status",
        "fields": {
            "OSLIP": {
                "bits": [ 0 ],
                "default": 0,
                "choices": [ "No Error", "DIR Output Data Slip/Repeat Error Detected" ],
                "desc": "Receiver Output Data Slip Error Status"
            },
        }
    },
    {   "name": "0x16",
        "regs": [ 0x16 ],
        "desc": "Receiver Interrupt Mask",
        "fields": {
            "MRBTI": {
                "bits": [ 0 ],
                "default": 0,
                "choices": [ "Masked", "Enabled" ],
                "desc": "Receiver Buffer Transfer Interrupt Mask"
            },
            "MQCRC": {
                "bits": [ 1 ],
                "default": 0,
                "choices": [ "Masked", "Enabled" ],
                "desc": "Q-Channel Sub-Code CRC Error Interrupt Mask"
            },
            "MUNLOCK": {
                "bits": [ 2 ],
                "default": 0,
                "choices": [ "Masked", "Enabled" ],
                "desc": "DIR Unlock Error Interrupt Mask"
            },
            "MQCHG": {
                "bits": [ 3 ],
                "default": 0,
                "choices": [ "Masked", "Enabled" ],
                "desc": "DIR Unlock Error Interrupt Mask"
            },
            "MBPERR": {
                "bits": [ 4 ],
                "default": 0,
                "choices": [ "Masked", "Enabled" ],
                "desc": "DIR Unlock Error Interrupt Mask"
            },
            "MVBIT": {
                "bits": [ 5 ],
                "default": 0,
                "choices": [ "Masked", "Enabled" ],
                "desc": "DIR Unlock Error Interrupt Mask"
            },
            "MPARITY": {
                "bits": [ 6 ],
                "default": 0,
                "choices": [ "Masked", "Enabled" ],
                "desc": "DIR Unlock Error Interrupt Mask"
            },
            "MCSCRC": {
                "bits": [ 7 ],
                "default": 0,
                "choices": [ "Masked", "Enabled" ],
                "desc": "Validity Error Interrupt Mask"
            },
        }
    },
    {   "name": "0x17",
        "regs": [ 0x17 ],
        "desc": "Receiver Interrupt Mask",
        "fields": {
            "MOSLIP": {
                "bits": [ 0 ],
                "default": 0,
                "choices": [ "Masked", "Enabled" ],
                "desc": "Receiver Output Data Slip Error Mask"
            },
        }
    },
    {   "name": "0x18",
        "regs": [ 0x18 ],
        "desc": "Receiver Interrupt Mode",
        "fields": {
            "RBTIM": {
                "bits": [ 0, 1 ],
                "default": 0,
                "choices": [ "Rising Edge Active", "Falling Edge Active", "Level Active", "Reserved" ],
                "desc": "Receive Buffer Transfer Interrupt Mode"
            },
            "QCRCM": {
                "bits": [ 2, 3 ],
                "default": 0,
                "choices": [ "Rising Edge Active", "Falling Edge Active", "Level Active", "Reserved" ],
                "desc": "Q-Channel Sub-Code CRC Error Interrupt Mode"
            },
            "UNLOCKM": {
                "bits": [ 4, 5 ],
                "default": 0,
                "choices": [ "Rising Edge Active", "Falling Edge Active", "Level Active", "Reserved" ],
                "desc": "DIR Unlock Error Interrupt Mode"
            },
            "QCHGM": {
                "bits": [ 6, 7 ],
                "default": 0,
                "choices": [ "Rising Edge Active", "Falling Edge Active", "Level Active", "Reserved" ],
                "desc": "Q-Channel Sub-Code Data Change Interrupt Mode"
            },
        }
    },
    {   "name": "0x19",
        "regs": [ 0x19 ],
        "desc": "Receiver Interrupt Mode",
        "fields": {
            "BPERRM": {
                "bits": [ 0, 1 ],
                "default": 0,
                "choices": [ "Rising Edge Active", "Falling Edge Active", "Level Active", "Reserved" ],
                "desc": "Bipolar Encoding Error Interrupt Mode"
            },
            "VBITM": {
                "bits": [ 2, 3 ],
                "default": 0,
                "choices": [ "Rising Edge Active", "Falling Edge Active", "Level Active", "Reserved" ],
                "desc": "Validity Error Interrupt Mode"
            },
            "PARITYM": {
                "bits": [ 4, 5 ],
                "default": 0,
                "choices": [ "Rising Edge Active", "Falling Edge Active", "Level Active", "Reserved" ],
                "desc": "Parity Error Interrupt Mode"
            },
            "CSCRCM": {
                "bits": [ 6, 7 ],
                "default": 0,
                "choices": [ "Rising Edge Active", "Falling Edge Active", "Level Active", "Reserved" ],
                "desc": "Channel Status CRC Error Interrupt Mode"
            },
        }
    },
    {   "name": "0x1A",
        "regs": [ 0x1A ],
        "desc": "Receiver Interrupt Mode",
        "fields": {
            "OSLIPM": {
                "bits": [ 0, 1 ],
                "default": 0,
                "choices": [ "Rising Edge Active", "Falling Edge Active", "Level Active", "Reserved" ],
                "desc": "Receiver Output Data Slip Error Interrupt Mode"
            },
        }
    },
    {   "name": "0x1B",
        "regs": [ 0x1B ],
        "desc": "General-Purpose Out (GPO1)",
        "fields": {
            "GPIO1": {
                "bits": [ 0, 1, 2, 3 ],
                "default": 0,
                "choices": [ "Forect Low", "Forced High", "SRC Interrupt (Active Low)", "Transmitter Interrupt (Active Low)", "Receiver Interrupt (Active Low)", "Receiver 50/15μs Pre-Emphasis (Active Low)", "Receiver Non-Audio Data (Active High)", "Receiver Non-Valid Data (Active High)", "Receiver Channel Status Bit", "Receiver User Data Bit", "Receiver Block Start Clock", "Receiver COPY Bit", "Receiver L-Bit", "Receiver Parity Error (Active High)", "Receiver Internal Sync Clock", "Transmitter Internal Sync Clock" ],
                "desc": "General-Purpose Output 1 (GPO1) Configuration"
            },
        }
    },
    {   "name": "0x1C",
        "regs": [ 0x1C ],
        "desc": "General-Purpose Out (GPO2)",
        "fields": {
            "GPIO2": {
                "bits": [ 0, 1, 2, 3 ],
                "default": 0,
                "choices": [ "Forect Low", "Forced High", "SRC Interrupt (Active Low)", "Transmitter Interrupt (Active Low)", "Receiver Interrupt (Active Low)", "Receiver 50/15μs Pre-Emphasis (Active Low)", "Receiver Non-Audio Data (Active High)", "Receiver Non-Valid Data (Active High)", "Receiver Channel Status Bit", "Receiver User Data Bit", "Receiver Block Start Clock", "Receiver COPY Bit", "Receiver L-Bit", "Receiver Parity Error (Active High)", "Receiver Internal Sync Clock", "Transmitter Internal Sync Clock" ],
                "desc": "General-Purpose Output 2 (GPO2) Configuration"
            },
        }
    },
    {   "name": "0x1D",
        "regs": [ 0x1D ],
        "desc": "General-Purpose Out (GPO3)",
        "fields": {
            "GPIO3": {
                "bits": [ 0, 1, 2, 3 ],
                "default": 0,
                "choices": [ "Forect Low", "Forced High", "SRC Interrupt (Active Low)", "Transmitter Interrupt (Active Low)", "Receiver Interrupt (Active Low)", "Receiver 50/15μs Pre-Emphasis (Active Low)", "Receiver Non-Audio Data (Active High)", "Receiver Non-Valid Data (Active High)", "Receiver Channel Status Bit", "Receiver User Data Bit", "Receiver Block Start Clock", "Receiver COPY Bit", "Receiver L-Bit", "Receiver Parity Error (Active High)", "Receiver Internal Sync Clock", "Transmitter Internal Sync Clock" ],
                "desc": "General-Purpose Output 3 (GPO3) Configuration"
            },
        }
    },
    {   "name": "0x1E",
        "regs": [ 0x1E ],
        "desc": "General-Purpose Out (GPO4)",
        "fields": {
            "GPIO4": {
                "bits": [ 0, 1, 2, 3 ],
                "default": 0,
                "choices": [ "Forect Low", "Forced High", "SRC Interrupt (Active Low)", "Transmitter Interrupt (Active Low)", "Receiver Interrupt (Active Low)", "Receiver 50/15μs Pre-Emphasis (Active Low)", "Receiver Non-Audio Data (Active High)", "Receiver Non-Valid Data (Active High)", "Receiver Channel Status Bit", "Receiver User Data Bit", "Receiver Block Start Clock", "Receiver COPY Bit", "Receiver L-Bit", "Receiver Parity Error (Active High)", "Receiver Internal Sync Clock", "Transmitter Internal Sync Clock" ],
                "desc": "General-Purpose Output 4 (GPO4) Configuration"
            },
        }
    },
    {   "name": "0x1F",
        "regs": [ 0x1F ],
        "desc": "Audio CD Q-Channel Sub-Code",
        "fields": {
            "Q7": {
                "bits": [ 0 ],
                "default": 0,
                "desc": ""
            },
            "Q6": {
                "bits": [ 1 ],
                "default": 0,
                "desc": ""
            },
            "Q5": {
                "bits": [ 2 ],
                "default": 0,
                "desc": ""
            },
            "Q4": {
                "bits": [ 3 ],
                "default": 0,
                "desc": ""
            },
            "Q3": {
                "bits": [ 4 ],
                "default": 0,
                "desc": ""
            },
            "Q2": {
                "bits": [ 5 ],
                "default": 0,
                "desc": ""
            },
            "Q1": {
                "bits": [ 6 ],
                "default": 0,
                "desc": ""
            },
            "Q0": {
                "bits": [ 7 ],
                "default": 0,
                "desc": ""
            },
        }
    },
    {   "name": "0x20",
        "regs": [ 0x20 ],
        "desc": "Audio CD Q-Channel Sub-Code",
        "fields": {
            "Q15": {
                "bits": [ 0 ],
                "default": 0,
                "desc": ""
            },
            "Q14": {
                "bits": [ 1 ],
                "default": 0,
                "desc": ""
            },
            "Q13": {
                "bits": [ 2 ],
                "default": 0,
                "desc": ""
            },
            "Q12": {
                "bits": [ 3 ],
                "default": 0,
                "desc": ""
            },
            "Q11": {
                "bits": [ 4 ],
                "default": 0,
                "desc": ""
            },
            "Q10": {
                "bits": [ 5 ],
                "default": 0,
                "desc": ""
            },
            "Q9": {
                "bits": [ 6 ],
                "default": 0,
                "desc": ""
            },
            "Q8": {
                "bits": [ 7 ],
                "default": 0,
                "desc": ""
            },
        }
    },
    {   "name": "0x21",
        "regs": [ 0x21 ],
        "desc": "Audio CD Q-Channel Sub-Code",
        "fields": {
            "Q23": {
                "bits": [ 0 ],
                "default": 0,
                "desc": ""
            },
            "Q22": {
                "bits": [ 1 ],
                "default": 0,
                "desc": ""
            },
            "Q21": {
                "bits": [ 2 ],
                "default": 0,
                "desc": ""
            },
            "Q20": {
                "bits": [ 3 ],
                "default": 0,
                "desc": ""
            },
            "Q19": {
                "bits": [ 4 ],
                "default": 0,
                "desc": ""
            },
            "Q18": {
                "bits": [ 5 ],
                "default": 0,
                "desc": ""
            },
            "Q17": {
                "bits": [ 6 ],
                "default": 0,
                "desc": ""
            },
            "Q16": {
                "bits": [ 7 ],
                "default": 0,
                "desc": ""
            },
        }
    },
    {   "name": "0x22",
        "regs": [ 0x22 ],
        "desc": "Audio CD Q-Channel Sub-Code",
        "fields": {
            "Q31": {
                "bits": [ 0 ],
                "default": 0,
                "desc": ""
            },
            "Q30": {
                "bits": [ 1 ],
                "default": 0,
                "desc": ""
            },
            "Q29": {
                "bits": [ 2 ],
                "default": 0,
                "desc": ""
            },
            "Q28": {
                "bits": [ 3 ],
                "default": 0,
                "desc": ""
            },
            "Q27": {
                "bits": [ 4 ],
                "default": 0,
                "desc": ""
            },
            "Q26": {
                "bits": [ 5 ],
                "default": 0,
                "desc": ""
            },
            "Q25": {
                "bits": [ 6 ],
                "default": 0,
                "desc": ""
            },
            "Q24": {
                "bits": [ 7 ],
                "default": 0,
                "desc": ""
            },
        }
    },
    {   "name": "0x23",
        "regs": [ 0x23 ],
        "desc": "Audio CD Q-Channel Sub-Code",
        "fields": {
            "Q39": {
                "bits": [ 0 ],
                "default": 0,
                "desc": ""
            },
            "Q38": {
                "bits": [ 1 ],
                "default": 0,
                "desc": ""
            },
            "Q37": {
                "bits": [ 2 ],
                "default": 0,
                "desc": ""
            },
            "Q36": {
                "bits": [ 3 ],
                "default": 0,
                "desc": ""
            },
            "Q35": {
                "bits": [ 4 ],
                "default": 0,
                "desc": ""
            },
            "Q34": {
                "bits": [ 5 ],
                "default": 0,
                "desc": ""
            },
            "Q33": {
                "bits": [ 6 ],
                "default": 0,
                "desc": ""
            },
            "Q32": {
                "bits": [ 7 ],
                "default": 0,
                "desc": ""
            },
        }
    },
    {   "name": "0x24",
        "regs": [ 0x24 ],
        "desc": "Audio CD Q-Channel Sub-Code",
        "fields": {
            "Q47": {
                "bits": [ 0 ],
                "default": 0,
                "desc": ""
            },
            "Q46": {
                "bits": [ 1 ],
                "default": 0,
                "desc": ""
            },
            "Q45": {
                "bits": [ 2 ],
                "default": 0,
                "desc": ""
            },
            "Q44": {
                "bits": [ 3 ],
                "default": 0,
                "desc": ""
            },
            "QQ43": {
                "bits": [ 4 ],
                "default": 0,
                "desc": ""
            },
            "Q42": {
                "bits": [ 5 ],
                "default": 0,
                "desc": ""
            },
            "Q41": {
                "bits": [ 6 ],
                "default": 0,
                "desc": ""
            },
            "Q40": {
                "bits": [ 7 ],
                "default": 0,
                "desc": ""
            },
        }
    },
    {   "name": "0x25",
        "regs": [ 0x25 ],
        "desc": "Audio CD Q-Channel Sub-Code",
        "fields": {
            "Q55": {
                "bits": [ 0 ],
                "default": 0,
                "desc": ""
            },
            "Q54": {
                "bits": [ 1 ],
                "default": 0,
                "desc": ""
            },
            "Q53": {
                "bits": [ 2 ],
                "default": 0,
                "desc": ""
            },
            "Q52": {
                "bits": [ 3 ],
                "default": 0,
                "desc": ""
            },
            "Q51": {
                "bits": [ 4 ],
                "default": 0,
                "desc": ""
            },
            "Q50": {
                "bits": [ 5 ],
                "default": 0,
                "desc": ""
            },
            "Q49": {
                "bits": [ 6 ],
                "default": 0,
                "desc": ""
            },
            "Q48": {
                "bits": [ 7 ],
                "default": 0,
                "desc": ""
            },
        }
    },
    {   "name": "0x26",
        "regs": [ 0x26 ],
        "desc": "Audio CD Q-Channel Sub-Code",
        "fields": {
            "Q63": {
                "bits": [ 0 ],
                "default": 0,
                "desc": ""
            },
            "Q62": {
                "bits": [ 1 ],
                "default": 0,
                "desc": ""
            },
            "Q61": {
                "bits": [ 2 ],
                "default": 0,
                "choices": [ "", "" ],
                "desc": ""
            },
            "Q60": {
                "bits": [ 3 ],
                "default": 0,
                "choices": [ "", "" ],
                "desc": ""
            },
            "Q59": {
                "bits": [ 4 ],
                "default": 0,
                "choices": [ "", "" ],
                "desc": ""
            },
            "Q58": {
                "bits": [ 5 ],
                "default": 0,
                "choices": [ "", "" ],
                "desc": ""
            },
            "Q57": {
                "bits": [ 6 ],
                "default": 0,
                "choices": [ "", "" ],
                "desc": ""
            },
            "Q56": {
                "bits": [ 7 ],
                "default": 0,
                "choices": [ "", "" ],
                "desc": ""
            },
        }
    },
    {   "name": "0x27",
        "regs": [ 0x27 ],
        "desc": "Audio CD Q-Channel Sub-Code",
        "fields": {
            "Q71": {
                "bits": [ 0 ],
                "default": 0,
                "desc": ""
            },
            "Q70": {
                "bits": [ 1 ],
                "default": 0,
                "desc": ""
            },
            "Q69": {
                "bits": [ 2 ],
                "default": 0,
                "desc": ""
            },
            "Q68": {
                "bits": [ 3 ],
                "default": 0,
                "desc": ""
            },
            "Q67": {
                "bits": [ 4 ],
                "default": 0,
                "desc": ""
            },
            "Q66": {
                "bits": [ 5 ],
                "default": 0,
                "desc": ""
            },
            "Q65": {
                "bits": [ 6 ],
                "default": 0,
                "desc": ""
            },
            "Q64": {
                "bits": [ 7 ],
                "default": 0,
                "desc": ""
            },
        }
    },
    {   "name": "0x28",
        "regs": [ 0x28 ],
        "desc": "Audio CD Q-Channel Sub-Code",
        "fields": {
            "Q79": {
                "bits": [ 0 ],
                "default": 0,
                "choices": [ "", "" ],
                "desc": ""
            },
            "Q78": {
                "bits": [ 1 ],
                "default": 0,
                "choices": [ "", "" ],
                "desc": ""
            },
            "Q77": {
                "bits": [ 2 ],
                "default": 0,
                "choices": [ "", "" ],
                "desc": ""
            },
            "Q76": {
                "bits": [ 3 ],
                "default": 0,
                "choices": [ "", "" ],
                "desc": ""
            },
            "Q75": {
                "bits": [ 4 ],
                "default": 0,
                "choices": [ "", "" ],
                "desc": ""
            },
            "Q74": {
                "bits": [ 5 ],
                "default": 0,
                "choices": [ "", "" ],
                "desc": ""
            },
            "Q73": {
                "bits": [ 6 ],
                "default": 0,
                "choices": [ "", "" ],
                "desc": ""
            },
            "Q72": {
                "bits": [ 7 ],
                "default": 0,
                "choices": [ "", "" ],
                "desc": ""
            },
        }
    },
    {   "name": "0x29-0x2A",
        "regs": [ 0x29, 0x2A  ],
        "desc": "PC Burst Preamble",
        "fields": {
            "PC_DATATYPE": {
                "bits": [ 0, 1, 2, 3, 4 ],
                "default": 0,
                "choices": [ "Null", "Dolby AC-3", "Reserved", "Pause", "MPEG-1 Layer 1", "MPEG-1 Layer 2 or 3 pr MPEG-3 Without Extension", "MPEG-2 Data With Extension", "MPEG-2 AAC ADTS", "MPEG-2 Layer 1 Low Sample Rate", "MPEG-2 Layer 2 or 3 Low Sample Rate", "Reserved", "DTS Type 1", "DTS Type 2", "DTS Type 3", "ATRAC", "ATRAC2/3", "Reserved", "Reserved", "Reserved", "Reserved", "Reserved", "Reserved", "Reserved", "Reserved", "Reserved", "Reserved", "Reserved", "Reserved", "Reserved", "Reserved", "Reserved", "Reserved" ],
                "desc": "PC Data Type"
            },
            "PC_ERROR": {
                "bits": [ 7 ],
                "default": 0,
                "choices": [ "Valid burst-payload", "Burst-payload may contain errors" ],
                "desc": "PC Error Flag"
            },
            "PC_DATA": {
                "bits": [ 8, 9, 10, 11, 12 ],
                "default": 0,
                "desc": "PC Error Flag"
            },
            "PC_STREAMNUMBER": {
                "bits": [ 13, 14, 15 ],
                "default": 0,
                "desc": "PC Stream Number"
            },
        }
    },
    {   "name": "0x2B-0x2C",
        "regs": [ 0x2B, 0x2C  ],
        "desc": "PD Burst Preamble",
        "fields": {
            "PD_LENGTH": {
                "bits": [ 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15 ],
                "default": 0,
                "desc": "PD Length of Burst"
            },
        }
    },
    {   "name": "0x2D",
        "regs": [ 0x2D ],
        "desc": "SRC Control",
        "fields": {
            "SRCIS": {
                "bits": [ 0, 1 ],
                "default": 0,
                "choices": [ "Port A", "Port B", "DIR", "Reserved" ],
                "desc": "SRC Input Data Source"
            },
            "SRCCLK": {
                "bits": [ 2, 3 ],
                "default": 0,
                "choices": [ "MCLK", "RXCKI", "RXCKO", "Reserved" ],
                "desc": "SRC Reference Clock Source"
            },
            "MUTE": {
                "bits": [ 4 ],
                "default": 0,
                "choices": [ "Unmeted", "Muted" ],
                "desc": "SRC Output Soft Mute Function"
            },
            "TRACK": {
                "bits": [ 6 ],
                "default": 0,
                "choices": [ "L/R independent attenuation", "R attenuation tracks L" ],
                "desc": "SRC Digital Output Attenuation Tracking"
            },
        }
    },
    {   "name": "0x2E",
        "regs": [ 0x2E ],
        "desc": "SRC Control",
        "fields": {
            "IGRP": {
                "bits": [ 0, 1 ],
                "default": 0,
                "choices": [ "64 Samples", "32 Samples", "16 Samples", "8 Samples" ],
                "desc": "SRC Interpolation Filter Group Delay"
            },
            "DDN": {
                "bits": [ 2 ],
                "default": 0,
                "choices": [ "Decimation Filter", "Direct Down Sampling" ],
                "desc": "SRC Decimation Filter/Direct Down-Sampling Function"
            },
            "DEM": {
                "bits": [ 3, 4 ],
                "default": 0,
                "choices": [ "De-Emphasis Disabled", "De-Emphasis Enabled for fS = 48kHz", "De-Emphasis Enabled for fS = 44.1kHz", "De-Emphasis Enabled for fS = 32kHz" ],
                "desc": "Digital De-Emphasis Filter, Manual Configuration"
            },
            "AUDODEM": {
                "bits": [ 5 ],
                "default": 0,
                "choices": [ "Disabled", "Enabled" ],
                "desc": "Automatic De-Emphasis Configuration"
            },
        }
    },
    {   "name": "0x2F",
        "regs": [ 0x2F ],
        "desc": "SRC Control Register 3",
        "fields": {
            "OWL": {
                "bits": [ 6, 7 ],
                "default": 0,
                "choices": [ "24 Bits", "20 Bits", "18 Bits", "16 Bits" ],
                "desc": "SRC Output Word Length"
            },
        }
    },
    {   "name": "0x30",
        "regs": [ 0x30 ],
        "desc": "SRC Control",
        "fields": {
            "AL": {
                "bits": [ 0, 1, 2, 3, 4, 5, 6, 7 ],
                "default": 0,
                "desc": "Left Channel Attenuation"
            },
        }
    },
    {   "name": "0x31",
        "regs": [ 0x31 ],
        "desc": "SRC Control",
        "fields": {
            "AR": {
                "bits": [ 0, 1, 2, 3, 4, 5, 6, 7 ],
                "default": 0,
                "desc": "Right Chennel Attenuation"
            },
        }
    },
    {   "name": "0x32-0x33",
        "regs": [ 0x32, 0x33 ],
        "desc": "SRC Input: Output Ratio",
        "fields": {
            "SRF": {
                "bits": [ 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10 ],
                "default": 0,
                "desc": "Fractional Part of the Input-to-Output Sampling Ratio"
            },
            "SRI": {
                "bits": [ 11, 12, 13, 14, 15 ],
                "default": 0,
                "desc": "Integer Part of the Input-to-Output Sampling Ratio"
            },
        }
    },
    {   "name": "0x7F",
        "regs": [ 0x7F ],
        "desc": "Page Selection",
        "fields": {
            "PAGE": {
                "bits": [ 0, 1 ],
                "default": 0,
                "choices": [ "Page 0, Control and Status Registers", "Page 1, DIR Channel Status and User Data Buffers", "Page 2, DIT Channel Status and User Data Buffers", "Page 3, Reserved" ],
                "desc": "Page Selection"
            },
        }
    },
)

def pdict(json_object:dict):
    print(str(json.dumps(json_object, indent=4)))

def i2c_reg_read(i2c:I2C, address:int, reg:int) -> int:
    msg_reg = [ I2C.Message([ reg ]) ]
    msg_read = [I2C.Message([ 0x00 ], read=True) ]
    i2c.transfer(address, msg_reg)
    i2c.transfer(address, msg_read)
    return msg_read[0].data[0]

def i2c_reg_write(i2c:I2C, address:int, reg:int, val:int) -> int:
    msg_reg_write = [ I2C.Message([ reg, val ]) ]
    i2c.transfer(address, msg_reg_write)
    return

def i2c_reg_read_multi(i2c:I2C, address:int, reg_first:int, reg_last:int) -> List[int]:
    return [ i2c_reg_read(i2c, address, reg) for reg in range(reg_first, reg_last+1) ]

# def reg_decode(reg_info:Dict) -> Dict:
def reg_decode(i2c:I2C, address:int, reg_info:Dict) -> Dict:
    val = 0
    for reg in reg_info["regs"]:
        vreg = i2c_reg_read(i2c, address, reg)
        val = val * 256 + vreg

    info = {
        # "name": reg_info["name"],
        "desc": reg_info["desc"],
        "value": val
    }
    if "fields" in reg_info:
        fields = {}
        sfields = {}
        
        # make sorted list
        field_bits = [ (-1, "") ] * (8*len(reg_info["regs"]))
        for i, key in enumerate(reg_info["fields"]):
            field_bits[reg_info["fields"][key]["bits"][0]] = (i,key)
            
        for ifield, key in field_bits:
            if key=="":
                continue
            vfield = 0
            for i, ibit in enumerate(reg_info["fields"][key]["bits"]):
                if val & (1<<ibit):
                    vfield += 1<<i
            fields[key] = vfield
            if "choices" in reg_info["fields"][key]:
                sfields[key] = reg_info["fields"][key]["choices"][vfield]
        info["fields"] = fields
        if len(sfields)>0:
            info["sfields"] = sfields
        
    return info
    
regs = {}
i2c=I2C("/dev/i2c-12")
regs[src4392_page0[0]["name"]] = reg_decode(i2c, 0x70, src4392_page0[0])
regs[src4392_page0[2]["name"]] = reg_decode(i2c, 0x70, src4392_page0[2])
regs[src4392_page0[3]["name"]] = reg_decode(i2c, 0x70, src4392_page0[3])
regs[src4392_page0[4]["name"]] = reg_decode(i2c, 0x70, src4392_page0[4])
regs[src4392_page0[5]["name"]] = reg_decode(i2c, 0x70, src4392_page0[5])
regs[src4392_page0[6]["name"]] = reg_decode(i2c, 0x70, src4392_page0[6])
regs[src4392_page0[7]["name"]] = reg_decode(i2c, 0x70, src4392_page0[7])
regs[src4392_page0[8]["name"]] = reg_decode(i2c, 0x70, src4392_page0[8])
regs[src4392_page0[9]["name"]] = reg_decode(i2c, 0x70, src4392_page0[9])
regs[src4392_page0[12]["name"]] = reg_decode(i2c, 0x70, src4392_page0[12])
regs[src4392_page0[13]["name"]] = reg_decode(i2c, 0x70, src4392_page0[13])
regs[src4392_page0[14]["name"]] = reg_decode(i2c, 0x70, src4392_page0[14])
regs[src4392_page0[15]["name"]] = reg_decode(i2c, 0x70, src4392_page0[15])
regs[src4392_page0[16]["name"]] = reg_decode(i2c, 0x70, src4392_page0[16])
regs[src4392_page0[17]["name"]] = reg_decode(i2c, 0x70, src4392_page0[17])
regs[src4392_page0[18]["name"]] = reg_decode(i2c, 0x70, src4392_page0[18])
regs[src4392_page0[39]["name"]] = reg_decode(i2c, 0x70, src4392_page0[39])
regs[src4392_page0[40]["name"]] = reg_decode(i2c, 0x70, src4392_page0[40])
regs[src4392_page0[41]["name"]] = reg_decode(i2c, 0x70, src4392_page0[41])
regs[src4392_page0[42]["name"]] = reg_decode(i2c, 0x70, src4392_page0[42])
regs[src4392_page0[43]["name"]] = reg_decode(i2c, 0x70, src4392_page0[43])
regs[src4392_page0[44]["name"]] = reg_decode(i2c, 0x70, src4392_page0[44])
i2c.close()

pdict(regs)
