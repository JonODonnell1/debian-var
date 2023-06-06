#!/bin/python3
from periphery import I2C
from typing import List, Tuple, Dict
import json
import sys

REG_FIELD={
    "bits": [ 0 ],       # low to high
    "value": 0,
    "default": 0,
    "choices": [ "OFF", "ON" ]
}
REG={   "name": "0x",
        "regs": [ 0 ],  # low to high
        "desc": "",
        "fields": {
            "field_name": REG_FIELD
        }
}

src4392_page0 = (
    {   "name": "0x01",     # Power-Down and Reset
        "regs": [ 0x01 ],
        "desc": "Power-Down and Reset",
        "fields": {
            "PDNSRCn": {
                "bits": [ 0 ],
                "choices": [ "Power Off", "Power On" ],
                "desc": "Power-Down for the SRC Function Block"
            },
            "PDNRXn": {
                "bits": [ 1 ],
                "choices": [ "Power Off", "Power On" ],
                "desc": "Power-Down for the Receiver Function Block"
            },
            "PDNTXn": {
                "bits": [ 2 ],
                "choices": [ "Power Off", "Power On" ],
                "desc": "Power-Down for the Transmitter Function Block"
            },
            "PDNPBn": {
                "bits": [ 3 ],
                "choices": [ "Power Off", "Power On" ],
                "desc": "Power-Down for Serial Port B"
            },
            "PDNPAn": {
                "bits": [ 4 ],
                "choices": [ "Power Off", "Power On" ],
                "desc": "Power-Down for Serial Port A"
            },
            "PDNALLn": {
                "bits": [ 5 ],
                "choices": [ "Power Off", "Power On" ],
                "desc": "Power-Down for All Functions"
            },
            "RESET": {
                "bits": [ 7 ],
                "choices": [ "SRC4392 Active", "Reset" ],
                "desc": "Software Reset"
            }
        }
    },
    {   "name": "0x02",     # Global Interrupt Status
        "regs": [ 0x02 ],
        "desc": "Global Interrupt Status",
        "fields": {
            "SRC": {
                "bits": [ 0 ],
                "desc": "SRC Function Block Interrupt Status (Active High)"
            },
            "RX": {
                "bits": [ 1 ],
                "desc": "Receiver Function Block Interrupt Status (Active High)"
            },
            "TX": {
                "bits": [ 2 ],
                "desc": "Transmitter Function Block Interrupt Status (Active High)"
            },
        }
    },
    {   "name": "0x03",     # Port A Control
        "regs": [ 0x03 ],
        "desc": "Port A Control",
        "fields": {
            "AFMT": {
                "bits": [ 0, 1, 2 ],
                "choices": [ "24-Bit Left-Justified", "24-Bit Phillips I2S", "Unused", "Unused", "16-Bit Right-Justified", "18-Bit Right-Justified", "20-Bit Right-Justified", "24-Bit Right-Justified" ],
                "desc": "Port A Audio Data Format"
            },
            "AM/S": {
                "bits": [ 3 ],
                "choices": [ "Slave mode", "Master mode" ],
                "desc": "Port A Slave/Master Mode"
            },
            "AOUTS": {
                "bits": [ 4, 5 ],
                "choices": [ "Port A Input", "Port B Input", "DIR", "SRC" ],
                "desc": "Port A Output Data Source"
            },
            "AMUTE": {
                "bits": [ 6 ],
                "choices": [ "Unmuted", "Muted" ],
                "desc": "Port A Output Mute"
            },
        }
    },
    {   "name": "0x04",     # Port A Control
        "regs": [ 0x04 ],
        "desc": "Port A Control",
        "fields": {
            "ADIV": {
                "bits": [ 0, 1 ],
                "choices": [ "Divide by 128", "Divide by 256", "Divide by 384", "Divide by 512" ],
                "desc": "Port A Master Clock Divider"
            },
            "ACLK": {
                "bits": [ 2, 3 ],
                "choices": [ "MCLK", "RXCKI", "RXCKO", "Reserved" ],
                "desc": "Port A Master Clock Source"
            },
        }
    },
    {   "name": "0x05",     # Port B Control
        "regs": [ 0x05 ],
        "desc": "Port B Control",
        "fields": {
            "BFMT": {
                "bits": [ 0, 1, 2 ],
                "choices": [ "24-Bit Left-Justified", "24-Bit Phillips I2S", "Unused", "Unused", "16-Bit Right-Justified", "18-Bit Right-Justified", "20-Bit Right-Justified", "24-Bit Right-Justified" ],
                "desc": "Port B Audio Data Format"
            },
            "BM/S": {
                "bits": [ 3 ],
                "choices": [ "Slave", "Master" ],
                "desc": "Port B Slave/Master Mode"
            },
            "BOUTS": {
                "bits": [ 4, 5 ],
                "choices": [ "Port B Input", "Part A Input", "DIR", "SRC" ],
                "desc": "Port B Output Source"
            },
            "BMUTE": {
                "bits": [ 6 ],
                "choices": [ "Unmuted", "Muted" ],
                "desc": "Port B Output Mute"
            },
        }
    },
    {   "name": "0x06",     # Port B Control
        "regs": [ 0x06 ],
        "desc": "Port B Control",
        "fields": {
            "BDIV": {
                "bits": [ 0, 1 ],
                "choices": [ "Divide by 128", "Divide by 256", "Divide by 384", "Divide by 512" ],
                "desc": "Port B Master Clock Divider"
            },
            "BCLK": {
                "bits": [ 2, 3 ],
                "choices": [ "MCLK", "RXCKI", "RXCKO", "Reserved" ],
                "desc": "Port B Master Clock Source"
            },
        }
    },
    {   "name": "0x07",     # Transmitter Control
        "regs": [ 0x07 ],
        "desc": "Transmitter Control",
        "fields": {
            "BSSL": {
                "bits": [ 0 ],
                "choices": [ "Data Slip Condition", "Block Start Condition" ],
                "desc": "Block Start or Asynchronous Data Slip Interrupt Trigger Selection"
            },
            "VALID": {
                "bits": [ 1 ],
                "choices": [ "Valid", "Invalid" ],
                "desc": "Validity (V) Data Bit"
            },
            "BLSM": {
                "bits": [ 2 ],
                "choices": [ "Input", "Output" ],
                "desc": "Transmitter Block Start Input/Output Mode"
            },
            "TXIS": {
                "bits": [ 3, 4 ],
                "choices": [ "Port A", "Port B", "DIR", "SRC" ],
                "desc": "Transmitter Input Data Source"
            },
            "TXDIV": {
                "bits": [ 5, 6 ],
                "choices": [ "Divide by 128", "Divide by 256", "Divide by 384", "Divide by 512" ],
                "desc": "Transmitter Master Clock Divider"
            },
            "TXCLK": {
                "bits": [ 7 ],
                "choices": [ "MCLK Input", "RXCKO" ],
                "desc": "Transmitter Master Clock Source"
            },
        }
    },
    {   "name": "0x08",     # Transmitter Control
        "regs": [ 0x08 ],
        "desc": "Transmitter Control",
        "fields": {
            "TXOFF": {
                "bits": [ 0 ],
                "choices": [ "Enabled", "Disabled" ],
                "desc": "Transmitter Line Driver Output Enable"
            },
            "TXMUTE": {
                "bits": [ 1 ],
                "choices": [ "Unmuted", "Muted" ],
                "desc": "Transmitter Audio Data Mute"
            },
            "AESOFF": {
                "bits": [ 2 ],
                "choices": [ "AES On", "AES Off" ],
                "desc": "AESOUT Output Enable"
            },
            "TXBTD": {
                "bits": [ 3 ],
                "choices": [ "Enabled", "Disabled" ],
                "desc": "Transmitter C and U Data Buffer Transfer Disable"
            },
            "LDMUX": {
                "bits": [ 4 ],
                "choices": [ "DIT AES3 Encoder Output", "Bypass Multiplexer Output" ],
                "desc": "Transmitter Line Driver Input Source Selection"
            },
            "AESMUX": {
                "bits": [ 5 ],
                "choices": [ "DIT AES3 Encoder Output", "Bypass Multiplexer Output" ],
                "desc": "AESOUT CMOS Buffer Input Source Selection"
            },
            "BYPMUX": {
                "bits": [ 6, 7 ],
                "choices": [ "RX1", "RX2", "RX3", "RX4" ],
                "desc": "Bypass Multiplexer Source Selection"
            },
        }
    },
    {   "name": "0x09",     # Transmitter Control
        "regs": [ 0x09 ],
        "desc": "Transmitter Control",
        "fields": {
            "TXCUS": {
                "bits": [ 0, 1 ],
                "choices": [ "Buffers not updated", "Updated via SPI or I2C", "Updated via DIR RA buffers", "first 10 bytes via SPI or I2C and remainder via DIR RA buffers" ],
                "desc": "Transmitter Channel Status and User Data Source"
            },
            "VALSEL": {
                "bits": [ 2 ],
                "choices": [ "VALID bit in control register 0x07", "bit is transferred from the DIR block with zero latency" ],
                "desc": "Transmitter Validity Bit Source"
            },
        }
    },
    {   "name": "0x0A",     # SRC and DIT Status
        "regs": [ 0x0A ],
        "desc": "SRC and DIT Status",
        "fields": {
            "TBTI": {
                "bits": [ 0 ],
                "desc": "Transmitter Buffer Transfer Status, Active High"
            },
            "TSLIP": {
                "bits": [ 1 ],
                "desc": "Transmitter Source Data Slip Status, Active High"
            },
            "READY": {
                "bits": [ 4 ],
                "desc": "SRC Rate Estimator Ready Status, Active High"
            },
            "RATIO": {
                "bits": [ 5 ],
                "desc": "SRC Ratio Status, Active High"
            },
        }
    },
    {   "name": "0x0B",     # SRC and DIT Interrupt Mask
        "regs": [ 0x0B ],
        "desc": "SRC and DIT Interrupt Mask",
        "fields": {
            "MTBTI": {
                "bits": [ 0 ],
                "choices": [ "BTI interrupt is masked", "BTI interrupt is enabled" ],
                "desc": "Transmitter Buffer Transfer Interrupt Mask"
            },
            "MTSLIP": {
                "bits": [ 1 ],
                "choices": [ "TSLIP interrupt is masked", "TSLIP interrupt is enabled" ],
                "desc": "Transmitter TSLIP Interrupt Mask"
            },
            "MREADY": {
                "bits": [ 4 ],
                "choices": [ "READY interrupt is masked", "READY interrupt is enabled" ],
                "desc": "SRC Ready Interrupt Mask"
            },
            "MRATIO": {
                "bits": [ 5 ],
                "choices": [ "RATIO interrupt is masked", "RATIO interrupt is enabled" ],
                "desc": "SRC Ratio Interrupt Mask"
            },
        }
    },
    {   "name": "0x0C",     # SRC and DIT Interrupt Mask
        "regs": [ 0x0C ],
        "desc": "SRC and DIT Interrupt Mask",
        "fields": {
            "TBTIM": {
                "bits": [ 0, 1 ],
                "choices": [ "Rising Edge Active", "Falling Edge Active", "Level Active", "Reserved" ],
                "desc": "Transmitter Buffer Transfer Interrupt Mode"
            },
            "TSLIPM": {
                "bits": [ 2, 3 ],
                "choices": [ "Rising Edge Active", "Falling Edge Active", "Level Active", "Reserved" ],
                "desc": "Transmitter Data Source Slip Interrupt Mode"
            },
            "READYM": {
                "bits": [ 4, 5 ],
                "choices": [ "Rising Edge Active", "Falling Edge Active", "Level Active", "Reserved" ],
                "desc": "SRC Ready Interrupt Mode"
            },
            "RATIOM": {
                "bits": [ 6, 7 ],
                "choices": [ "Rising Edge Active", "Falling Edge Active", "Level Active", "Reserved" ],
                "desc": "SRC Ratio Interrupt Mode"
            },
        }
    },
    {   "name": "0x0D",     # Receiver Control
        "regs": [ 0x0D ],
        "desc": "Receiver Control",
        "fields": {
            "RXMUX": {
                "bits": [ 0, 1 ],
                "choices": [ "RX1", "RX2", "RX3", "RX4" ],
                "desc": "Receiver Input Source Selection"
            },
            "RXCLK": {
                "bits": [ 3 ],
                "choices": [ "RXCKI", "MCLK" ],
                "desc": "Receiver Reference Clock Source"
            },
            "RXBTD": {
                "bits": [ 4 ],
                "choices": [ "Enabled", "Disabled; the user may read C and U data from the DIR UA buffers" ],
                "desc": "Receiver C and U Data Buffer Transfer Disable"
            },
        }
    },
    {   "name": "0x0E",     # Receiver Control
        "regs": [ 0x0E ],
        "desc": "Receiver Control",
        "fields": {
            "RXCKOE": {
                "bits": [ 0 ],
                "choices": [ "Disabled; the RXCKO output is set to high-impedance", "Enabled; the recovered master clock is available at RXCKO" ],
                "desc": "RXCKOE Output Enable"
            },
            "RXCKOD": {
                "bits": [ 1, 2 ],
                "choices": [ "Passthrough", "PLL2 / 2", "PLL2 / 4", "PLL2 / 8" ],
                "desc": "RXCKO Output Clock Divider"
            },
            "RXAMLL": {
                "bits": [ 3 ],
                "choices": [ "Disabled", "Enabled; MUTE on LOL" ],
                "desc": "Receiver Automatic Mute for Loss of Lock"
            },
            "LOL": {
                "bits": [ 4 ],
                "choices": [ "PLL2 output clock is stopped for LOL", "PLL2 output clock free runs when LOL" ],
                "desc": "Receiver Loss of Lock Mode for the Recovered Clock (output from PLL2)"
            },
        }
    },
    {   "name": "0x0F-0x11",# Receiver PLL Configuration
        "regs": [ 0x0F, 0x10, 0x11 ],
        "desc": "Receiver PLL Configuration",
        "fields": {
            "D": {
                "bits": [ 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13 ],
                "desc": "Fractional part (0-9999) of K=J.D"
            },
            "J": {
                "bits": [ 14, 15, 16, 17, 18, 19 ],
                "desc": "Integer part (1 to 63) of K=J.D"
            },
            "P": {
                "bits": [ 20, 21, 22, 23 ],
                "desc": "Pre-Divider (1-7)"
            },
        }
    },
    {   "name": "0x12",     # Non-PCM Audio Detection
        "regs": [ 0x12 ],
        "desc": "Non-PCM Audio Detection",
        "fields": {
            "IEC61937": {
                "bits": [ 0 ],
                "choices": [ "Not an IEC61937 format", "IEC61937 format" ],
                "desc": "Indicates detection of an IEC 61937 data"
            },
            "DTS CD/LD": {
                "bits": [ 1 ],
                "choices": [ "CD/LD is not DTS encoded", "DTS CD/LD playback detected" ],
                "desc": "indicates detection of a DTS encoded audio"
            },
        }
    },
    {   "name": "0x13",     # Receiver Status
        "regs": [ 0x13 ],
        "desc": "Receiver Status",
        "fields": {
            "RXCKR": {
                "bits": [ 0, 1 ],
                "choices": [ "Clock rate not determined", "128fs", "256fs", "512fs" ],
                "desc": "Maximum Available Recovered Clock Rate"
            },
        }
    },
    {   "name": "0x14",     # Receiver Status
        "regs": [ 0x14 ],
        "desc": "Receiver Status",
        "fields": {
            "RBTI": {
                "bits": [ 0 ],
                "choices": [ "Buffer Transfer Incomplete, or No Buffer Transfer Interrupt Indicated", "Buffer Transfer Completed" ],
                "desc": "Receiver Buffer Transfer Interrupt Status"
            },
            "QCRC": {
                "bits": [ 1 ],
                "choices": [ "No Error", "Q-channel sub-code data CRC error detected" ],
                "desc": "Q-Channel Sub-Code CRC Status"
            },
            "UNLOCK": {
                "bits": [ 2 ],
                "choices": [ "No error; the DIR AES3 decoder and PLL2 are locked", "DIR lock error; the AES3 decoder and PLL2 are unlocked" ],
                "desc": "DIR Unlock Error Status"
            },
            "QCHG": {
                "bits": [ 3 ],
                "choices": [ "No change in Q-channel sub-code data", "Q-channel data has changed" ],
                "desc": "Q-Channel Sub-Code Data Change Status"
            },
            "BPERR": {
                "bits": [ 4 ],
                "choices": [ "No Error", "Bipolar Encoding Error Detected" ],
                "desc": "Bipolar Encoding Error Status"
            },
            "VBIT": {
                "bits": [ 5 ],
                "choices": [ "Valid Audio Data Indicated", "Non-Valid Data Indicated" ],
                "desc": "Validity Bit Status"
            },
            "PARITY": {
                "bits": [ 6 ],
                "choices": [ "No Error", "Parity Error Detected" ],
                "desc": "Parity Status"
            },
            "CSCRC": {
                "bits": [ 7 ],
                "choices": [ "No Error", "CRC Error Detected" ],
                "desc": "Channel Status CRC Status"
            },
        }
    },
    {   "name": "0x15",     # Receiver Status
        "regs": [ 0x15 ],
        "desc": "Receiver Status",
        "fields": {
            "OSLIP": {
                "bits": [ 0 ],
                "choices": [ "No Error", "DIR Output Data Slip/Repeat Error Detected" ],
                "desc": "Receiver Output Data Slip Error Status"
            },
        }
    },
    {   "name": "0x16",     # Receiver Interrupt Mask
        "regs": [ 0x16 ],
        "desc": "Receiver Interrupt Mask",
        "fields": {
            "MRBTI": {
                "bits": [ 0 ],
                "choices": [ "Masked", "Enabled" ],
                "desc": "Receiver Buffer Transfer Interrupt Mask"
            },
            "MQCRC": {
                "bits": [ 1 ],
                "choices": [ "Masked", "Enabled" ],
                "desc": "Q-Channel Sub-Code CRC Error Interrupt Mask"
            },
            "MUNLOCK": {
                "bits": [ 2 ],
                "choices": [ "Masked", "Enabled" ],
                "desc": "DIR Unlock Error Interrupt Mask"
            },
            "MQCHG": {
                "bits": [ 3 ],
                "choices": [ "Masked", "Enabled" ],
                "desc": "DIR Unlock Error Interrupt Mask"
            },
            "MBPERR": {
                "bits": [ 4 ],
                "choices": [ "Masked", "Enabled" ],
                "desc": "DIR Unlock Error Interrupt Mask"
            },
            "MVBIT": {
                "bits": [ 5 ],
                "choices": [ "Masked", "Enabled" ],
                "desc": "DIR Unlock Error Interrupt Mask"
            },
            "MPARITY": {
                "bits": [ 6 ],
                "choices": [ "Masked", "Enabled" ],
                "desc": "DIR Unlock Error Interrupt Mask"
            },
            "MCSCRC": {
                "bits": [ 7 ],
                "choices": [ "Masked", "Enabled" ],
                "desc": "Validity Error Interrupt Mask"
            },
        }
    },
    {   "name": "0x17",     # Receiver Interrupt Mask
        "regs": [ 0x17 ],
        "desc": "Receiver Interrupt Mask",
        "fields": {
            "MOSLIP": {
                "bits": [ 0 ],
                "choices": [ "Masked", "Enabled" ],
                "desc": "Receiver Output Data Slip Error Mask"
            },
        }
    },
    {   "name": "0x18",     # Receiver Interrupt Mode
        "regs": [ 0x18 ],
        "desc": "Receiver Interrupt Mode",
        "fields": {
            "RBTIM": {
                "bits": [ 0, 1 ],
                "choices": [ "Rising Edge Active", "Falling Edge Active", "Level Active", "Reserved" ],
                "desc": "Receive Buffer Transfer Interrupt Mode"
            },
            "QCRCM": {
                "bits": [ 2, 3 ],
                "choices": [ "Rising Edge Active", "Falling Edge Active", "Level Active", "Reserved" ],
                "desc": "Q-Channel Sub-Code CRC Error Interrupt Mode"
            },
            "UNLOCKM": {
                "bits": [ 4, 5 ],
                "choices": [ "Rising Edge Active", "Falling Edge Active", "Level Active", "Reserved" ],
                "desc": "DIR Unlock Error Interrupt Mode"
            },
            "QCHGM": {
                "bits": [ 6, 7 ],
                "choices": [ "Rising Edge Active", "Falling Edge Active", "Level Active", "Reserved" ],
                "desc": "Q-Channel Sub-Code Data Change Interrupt Mode"
            },
        }
    },
    {   "name": "0x19",     # Receiver Interrupt Mode
        "regs": [ 0x19 ],
        "desc": "Receiver Interrupt Mode",
        "fields": {
            "BPERRM": {
                "bits": [ 0, 1 ],
                "choices": [ "Rising Edge Active", "Falling Edge Active", "Level Active", "Reserved" ],
                "desc": "Bipolar Encoding Error Interrupt Mode"
            },
            "VBITM": {
                "bits": [ 2, 3 ],
                "choices": [ "Rising Edge Active", "Falling Edge Active", "Level Active", "Reserved" ],
                "desc": "Validity Error Interrupt Mode"
            },
            "PARITYM": {
                "bits": [ 4, 5 ],
                "choices": [ "Rising Edge Active", "Falling Edge Active", "Level Active", "Reserved" ],
                "desc": "Parity Error Interrupt Mode"
            },
            "CSCRCM": {
                "bits": [ 6, 7 ],
                "choices": [ "Rising Edge Active", "Falling Edge Active", "Level Active", "Reserved" ],
                "desc": "Channel Status CRC Error Interrupt Mode"
            },
        }
    },
    {   "name": "0x1A",     # Receiver Interrupt Mode
        "regs": [ 0x1A ],
        "desc": "Receiver Interrupt Mode",
        "fields": {
            "OSLIPM": {
                "bits": [ 0, 1 ],
                "choices": [ "Rising Edge Active", "Falling Edge Active", "Level Active", "Reserved" ],
                "desc": "Receiver Output Data Slip Error Interrupt Mode"
            },
        }
    },
    {   "name": "0x1B",     # General-Purpose Out (GPO1)
        "regs": [ 0x1B ],
        "desc": "General-Purpose Out (GPO1)",
        "fields": {
            "GPIO1": {
                "bits": [ 0, 1, 2, 3 ],
                "choices": [ "Forect Low", "Forced High", "SRC Interrupt (Active Low)", "Transmitter Interrupt (Active Low)", "Receiver Interrupt (Active Low)", "Receiver 50/15μs Pre-Emphasis (Active Low)", "Receiver Non-Audio Data (Active High)", "Receiver Non-Valid Data (Active High)", "Receiver Channel Status Bit", "Receiver User Data Bit", "Receiver Block Start Clock", "Receiver COPY Bit", "Receiver L-Bit", "Receiver Parity Error (Active High)", "Receiver Internal Sync Clock", "Transmitter Internal Sync Clock" ],
                "desc": "General-Purpose Output 1 (GPO1) Configuration"
            },
        }
    },
    {   "name": "0x1C",     # General-Purpose Out (GPO2)
        "regs": [ 0x1C ],
        "desc": "General-Purpose Out (GPO2)",
        "fields": {
            "GPIO2": {
                "bits": [ 0, 1, 2, 3 ],
                "choices": [ "Forect Low", "Forced High", "SRC Interrupt (Active Low)", "Transmitter Interrupt (Active Low)", "Receiver Interrupt (Active Low)", "Receiver 50/15μs Pre-Emphasis (Active Low)", "Receiver Non-Audio Data (Active High)", "Receiver Non-Valid Data (Active High)", "Receiver Channel Status Bit", "Receiver User Data Bit", "Receiver Block Start Clock", "Receiver COPY Bit", "Receiver L-Bit", "Receiver Parity Error (Active High)", "Receiver Internal Sync Clock", "Transmitter Internal Sync Clock" ],
                "desc": "General-Purpose Output 2 (GPO2) Configuration"
            },
        }
    },
    {   "name": "0x1D",     # General-Purpose Out (GPO3)
        "regs": [ 0x1D ],
        "desc": "General-Purpose Out (GPO3)",
        "fields": {
            "GPIO3": {
                "bits": [ 0, 1, 2, 3 ],
                "choices": [ "Forect Low", "Forced High", "SRC Interrupt (Active Low)", "Transmitter Interrupt (Active Low)", "Receiver Interrupt (Active Low)", "Receiver 50/15μs Pre-Emphasis (Active Low)", "Receiver Non-Audio Data (Active High)", "Receiver Non-Valid Data (Active High)", "Receiver Channel Status Bit", "Receiver User Data Bit", "Receiver Block Start Clock", "Receiver COPY Bit", "Receiver L-Bit", "Receiver Parity Error (Active High)", "Receiver Internal Sync Clock", "Transmitter Internal Sync Clock" ],
                "desc": "General-Purpose Output 3 (GPO3) Configuration"
            },
        }
    },
    {   "name": "0x1E",     # General-Purpose Out (GPO4)
        "regs": [ 0x1E ],
        "desc": "General-Purpose Out (GPO4)",
        "fields": {
            "GPIO4": {
                "bits": [ 0, 1, 2, 3 ],
                "choices": [ "Forect Low", "Forced High", "SRC Interrupt (Active Low)", "Transmitter Interrupt (Active Low)", "Receiver Interrupt (Active Low)", "Receiver 50/15μs Pre-Emphasis (Active Low)", "Receiver Non-Audio Data (Active High)", "Receiver Non-Valid Data (Active High)", "Receiver Channel Status Bit", "Receiver User Data Bit", "Receiver Block Start Clock", "Receiver COPY Bit", "Receiver L-Bit", "Receiver Parity Error (Active High)", "Receiver Internal Sync Clock", "Transmitter Internal Sync Clock" ],
                "desc": "General-Purpose Output 4 (GPO4) Configuration"
            },
        }
    },
    {   "name": "0x1F",     # Audio CD Q-Channel Sub-Code
        "regs": [ 0x1F ],
        "desc": "Audio CD Q-Channel Sub-Code",
        "fields": {
            "Q7": {
                "bits": [ 0 ],
                "desc": ""
            },
            "Q6": {
                "bits": [ 1 ],
                "desc": ""
            },
            "Q5": {
                "bits": [ 2 ],
                "desc": ""
            },
            "Q4": {
                "bits": [ 3 ],
                "desc": ""
            },
            "Q3": {
                "bits": [ 4 ],
                "desc": ""
            },
            "Q2": {
                "bits": [ 5 ],
                "desc": ""
            },
            "Q1": {
                "bits": [ 6 ],
                "desc": ""
            },
            "Q0": {
                "bits": [ 7 ],
                "desc": ""
            },
        }
    },
    {   "name": "0x20",     # Audio CD Q-Channel Sub-Code
        "regs": [ 0x20 ],
        "desc": "Audio CD Q-Channel Sub-Code",
        "fields": {
            "Q15": {
                "bits": [ 0 ],
                "desc": ""
            },
            "Q14": {
                "bits": [ 1 ],
                "desc": ""
            },
            "Q13": {
                "bits": [ 2 ],
                "desc": ""
            },
            "Q12": {
                "bits": [ 3 ],
                "desc": ""
            },
            "Q11": {
                "bits": [ 4 ],
                "desc": ""
            },
            "Q10": {
                "bits": [ 5 ],
                "desc": ""
            },
            "Q9": {
                "bits": [ 6 ],
                "desc": ""
            },
            "Q8": {
                "bits": [ 7 ],
                "desc": ""
            },
        }
    },
    {   "name": "0x21",     # Audio CD Q-Channel Sub-Code
        "regs": [ 0x21 ],
        "desc": "Audio CD Q-Channel Sub-Code",
        "fields": {
            "Q23": {
                "bits": [ 0 ],
                "desc": ""
            },
            "Q22": {
                "bits": [ 1 ],
                "desc": ""
            },
            "Q21": {
                "bits": [ 2 ],
                "desc": ""
            },
            "Q20": {
                "bits": [ 3 ],
                "desc": ""
            },
            "Q19": {
                "bits": [ 4 ],
                "desc": ""
            },
            "Q18": {
                "bits": [ 5 ],
                "desc": ""
            },
            "Q17": {
                "bits": [ 6 ],
                "desc": ""
            },
            "Q16": {
                "bits": [ 7 ],
                "desc": ""
            },
        }
    },
    {   "name": "0x22",     # Audio CD Q-Channel Sub-Code
        "regs": [ 0x22 ],
        "desc": "Audio CD Q-Channel Sub-Code",
        "fields": {
            "Q31": {
                "bits": [ 0 ],
                "desc": ""
            },
            "Q30": {
                "bits": [ 1 ],
                "desc": ""
            },
            "Q29": {
                "bits": [ 2 ],
                "desc": ""
            },
            "Q28": {
                "bits": [ 3 ],
                "desc": ""
            },
            "Q27": {
                "bits": [ 4 ],
                "desc": ""
            },
            "Q26": {
                "bits": [ 5 ],
                "desc": ""
            },
            "Q25": {
                "bits": [ 6 ],
                "desc": ""
            },
            "Q24": {
                "bits": [ 7 ],
                "desc": ""
            },
        }
    },
    {   "name": "0x23",     # Audio CD Q-Channel Sub-Code
        "regs": [ 0x23 ],
        "desc": "Audio CD Q-Channel Sub-Code",
        "fields": {
            "Q39": {
                "bits": [ 0 ],
                "desc": ""
            },
            "Q38": {
                "bits": [ 1 ],
                "desc": ""
            },
            "Q37": {
                "bits": [ 2 ],
                "desc": ""
            },
            "Q36": {
                "bits": [ 3 ],
                "desc": ""
            },
            "Q35": {
                "bits": [ 4 ],
                "desc": ""
            },
            "Q34": {
                "bits": [ 5 ],
                "desc": ""
            },
            "Q33": {
                "bits": [ 6 ],
                "desc": ""
            },
            "Q32": {
                "bits": [ 7 ],
                "desc": ""
            },
        }
    },
    {   "name": "0x24",     # Audio CD Q-Channel Sub-Code
        "regs": [ 0x24 ],
        "desc": "Audio CD Q-Channel Sub-Code",
        "fields": {
            "Q47": {
                "bits": [ 0 ],
                "desc": ""
            },
            "Q46": {
                "bits": [ 1 ],
                "desc": ""
            },
            "Q45": {
                "bits": [ 2 ],
                "desc": ""
            },
            "Q44": {
                "bits": [ 3 ],
                "desc": ""
            },
            "QQ43": {
                "bits": [ 4 ],
                "desc": ""
            },
            "Q42": {
                "bits": [ 5 ],
                "desc": ""
            },
            "Q41": {
                "bits": [ 6 ],
                "desc": ""
            },
            "Q40": {
                "bits": [ 7 ],
                "desc": ""
            },
        }
    },
    {   "name": "0x25",     # Audio CD Q-Channel Sub-Code
        "regs": [ 0x25 ],
        "desc": "Audio CD Q-Channel Sub-Code",
        "fields": {
            "Q55": {
                "bits": [ 0 ],
                "desc": ""
            },
            "Q54": {
                "bits": [ 1 ],
                "desc": ""
            },
            "Q53": {
                "bits": [ 2 ],
                "desc": ""
            },
            "Q52": {
                "bits": [ 3 ],
                "desc": ""
            },
            "Q51": {
                "bits": [ 4 ],
                "desc": ""
            },
            "Q50": {
                "bits": [ 5 ],
                "desc": ""
            },
            "Q49": {
                "bits": [ 6 ],
                "desc": ""
            },
            "Q48": {
                "bits": [ 7 ],
                "desc": ""
            },
        }
    },
    {   "name": "0x26",     # Audio CD Q-Channel Sub-Code
        "regs": [ 0x26 ],
        "desc": "Audio CD Q-Channel Sub-Code",
        "fields": {
            "Q63": {
                "bits": [ 0 ],
                "desc": ""
            },
            "Q62": {
                "bits": [ 1 ],
                "desc": ""
            },
            "Q61": {
                "bits": [ 2 ],
                "desc": ""
            },
            "Q60": {
                "bits": [ 3 ],
                "desc": ""
            },
            "Q59": {
                "bits": [ 4 ],
                "desc": ""
            },
            "Q58": {
                "bits": [ 5 ],
                "desc": ""
            },
            "Q57": {
                "bits": [ 6 ],
                "desc": ""
            },
            "Q56": {
                "bits": [ 7 ],
                "desc": ""
            },
        }
    },
    {   "name": "0x27",     # Audio CD Q-Channel Sub-Code
        "regs": [ 0x27 ],
        "desc": "Audio CD Q-Channel Sub-Code",
        "fields": {
            "Q71": {
                "bits": [ 0 ],
                "desc": ""
            },
            "Q70": {
                "bits": [ 1 ],
                "desc": ""
            },
            "Q69": {
                "bits": [ 2 ],
                "desc": ""
            },
            "Q68": {
                "bits": [ 3 ],
                "desc": ""
            },
            "Q67": {
                "bits": [ 4 ],
                "desc": ""
            },
            "Q66": {
                "bits": [ 5 ],
                "desc": ""
            },
            "Q65": {
                "bits": [ 6 ],
                "desc": ""
            },
            "Q64": {
                "bits": [ 7 ],
                "desc": ""
            },
        }
    },
    {   "name": "0x28",     # Audio CD Q-Channel Sub-Code
        "regs": [ 0x28 ],
        "desc": "Audio CD Q-Channel Sub-Code",
        "fields": {
            "Q79": {
                "bits": [ 0 ],
                "desc": ""
            },
            "Q78": {
                "bits": [ 1 ],
                "desc": ""
            },
            "Q77": {
                "bits": [ 2 ],
                "desc": ""
            },
            "Q76": {
                "bits": [ 3 ],
                "desc": ""
            },
            "Q75": {
                "bits": [ 4 ],
                "desc": ""
            },
            "Q74": {
                "bits": [ 5 ],
                "desc": ""
            },
            "Q73": {
                "bits": [ 6 ],
                "desc": ""
            },
            "Q72": {
                "bits": [ 7 ],
                "desc": ""
            },
        }
    },
    {   "name": "0x29-0x2A",# PC Burst Preamble
        "regs": [ 0x29, 0x2A  ],
        "desc": "PC Burst Preamble",
        "fields": {
            "PC_DATATYPE": {
                "bits": [ 0, 1, 2, 3, 4 ],
                "choices": [ "Null", "Dolby AC-3", "Reserved", "Pause", "MPEG-1 Layer 1", "MPEG-1 Layer 2 or 3 pr MPEG-3 Without Extension", "MPEG-2 Data With Extension", "MPEG-2 AAC ADTS", "MPEG-2 Layer 1 Low Sample Rate", "MPEG-2 Layer 2 or 3 Low Sample Rate", "Reserved", "DTS Type 1", "DTS Type 2", "DTS Type 3", "ATRAC", "ATRAC2/3", "Reserved", "Reserved", "Reserved", "Reserved", "Reserved", "Reserved", "Reserved", "Reserved", "Reserved", "Reserved", "Reserved", "Reserved", "Reserved", "Reserved", "Reserved", "Reserved" ],
                "desc": "PC Data Type"
            },
            "PC_ERROR": {
                "bits": [ 7 ],
                "choices": [ "Valid burst-payload", "Burst-payload may contain errors" ],
                "desc": "PC Error Flag"
            },
            "PC_DATA": {
                "bits": [ 8, 9, 10, 11, 12 ],
                "desc": "PC Error Flag"
            },
            "PC_STREAMNUMBER": {
                "bits": [ 13, 14, 15 ],
                "desc": "PC Stream Number"
            },
        }
    },
    {   "name": "0x2B-0x2C",# PD Burst Preamble
        "regs": [ 0x2B, 0x2C  ],
        "desc": "PD Burst Preamble",
        "fields": {
            "PD_LENGTH": {
                "bits": [ 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15 ],
                "desc": "PD Length of Burst"
            },
        }
    },
    {   "name": "0x2D",     # SRC Control
        "regs": [ 0x2D ],
        "desc": "SRC Control",
        "fields": {
            "SRCIS": {
                "bits": [ 0, 1 ],
                "choices": [ "Port A", "Port B", "DIR", "Reserved" ],
                "desc": "SRC Input Data Source"
            },
            "SRCCLK": {
                "bits": [ 2, 3 ],
                "choices": [ "MCLK", "RXCKI", "RXCKO", "Reserved" ],
                "desc": "SRC Reference Clock Source"
            },
            "MUTE": {
                "bits": [ 4 ],
                "choices": [ "Unmuted", "Muted" ],
                "desc": "SRC Output Soft Mute Function"
            },
            "TRACK": {
                "bits": [ 6 ],
                "choices": [ "L/R independent attenuation", "R attenuation tracks L" ],
                "desc": "SRC Digital Output Attenuation Tracking"
            },
        }
    },
    {   "name": "0x2E",     # SRC Control
        "regs": [ 0x2E ],
        "desc": "SRC Control",
        "fields": {
            "IGRP": {
                "bits": [ 0, 1 ],
                "choices": [ "64 Samples", "32 Samples", "16 Samples", "8 Samples" ],
                "desc": "SRC Interpolation Filter Group Delay"
            },
            "DDN": {
                "bits": [ 2 ],
                "choices": [ "Decimation Filter", "Direct Down Sampling" ],
                "desc": "SRC Decimation Filter/Direct Down-Sampling Function"
            },
            "DEM": {
                "bits": [ 3, 4 ],
                "choices": [ "De-Emphasis Disabled", "De-Emphasis Enabled for fS = 48kHz", "De-Emphasis Enabled for fS = 44.1kHz", "De-Emphasis Enabled for fS = 32kHz" ],
                "desc": "Digital De-Emphasis Filter, Manual Configuration"
            },
            "AUDODEM": {
                "bits": [ 5 ],
                "choices": [ "Disabled", "Enabled" ],
                "desc": "Automatic De-Emphasis Configuration"
            },
        }
    },
    {   "name": "0x2F",     # SRC Control Register 3
        "regs": [ 0x2F ],
        "desc": "SRC Control Register 3",
        "fields": {
            "OWL": {
                "bits": [ 6, 7 ],
                "choices": [ "24 Bits", "20 Bits", "18 Bits", "16 Bits" ],
                "desc": "SRC Output Word Length"
            },
        }
    },
    {   "name": "0x30",     # SRC Control Left Attenuation
        "regs": [ 0x30 ],
        "desc": "SRC Control",
        "fields": {
            "AL": {
                "bits": [ 0, 1, 2, 3, 4, 5, 6, 7 ],
                "desc": "Left Channel Attenuation"
            },
        }
    },
    {   "name": "0x31",     # SRC Control Right Attenuation
        "regs": [ 0x31 ],
        "desc": "SRC Control",
        "fields": {
            "AR": {
                "bits": [ 0, 1, 2, 3, 4, 5, 6, 7 ],
                "desc": "Right Channel Attenuation"
            },
        }
    },
    {   "name": "0x32-0x33",# SRC Input: Output Ratio
        "regs": [ 0x32, 0x33 ],
        "desc": "SRC Input: Output Ratio",
        "fields": {
            "SRF": {
                "bits": [ 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10 ],
                "desc": "Fractional Part of the Input-to-Output Sampling Ratio"
            },
            "SRI": {
                "bits": [ 11, 12, 13, 14, 15 ],
                "desc": "Integer Part of the Input-to-Output Sampling Ratio"
            },
        }
    },
    {   "name": "0x7F",     # Page Selection
        "regs": [ 0x7F ],
        "desc": "Page Selection",
        "fields": {
            "PAGE": {
                "bits": [ 0, 1 ],
                "choices": [ "Page 0, Control and Status Registers", "Page 1, DIR Channel Status and User Data Buffers", "Page 2, DIT Channel Status and User Data Buffers", "Page 3, Reserved" ],
                "desc": "Page Selection"
            },
        }
    },
)

src4392_page1 = (
    {   "name": "0x00",     # DIR Channel Status Ch1 Byte 0
        "regs": [ 0x00 ],
        "desc": "DIR Channel Status Ch1 Byte 0",
        "fields": {
            "FORMAT": {
                "bits": [ 7 ],
                "choices": [ "S/PDIF", "AES3" ],
                "desc": "Data format"
            },
            "MODE": {
                "bits": [ 6 ],
                "choices": [ "Digital Audio", "Non-Audio" ],
                "desc": "Data mode"
            },
            "SCMS": {
                "bits": [ 5 ],
                "choices": [ "Copy Restricted", "Copy Permitted" ],
                "desc": "Copy protection"
            },
            "PREEMPHASIS": {
                "bits": [ 4, 3, 2 ],
                "choices": [ "None - 2ch", "50/10us - 2ch", "Reserved - 2 ch", "Reserved - 2ch", "Reserved - 4ch", "Reserved - 4ch", "Reserved - 4ch", "Reserved - 4ch" ],
                "desc": "Pre-emphasis"
            },
        }
    },
    {   "name": "0x01",     # DIR Channel Status Ch2 Byte 0
        "regs": [ 0x01 ],
        "desc": "DIR Channel Status Ch2 Byte 0",
        "fields": {
            "FORMAT": {
                "bits": [ 7 ],
                "choices": [ "S/PDIF", "AES3" ],
                "desc": "Data format"
            },
            "MODE": {
                "bits": [ 6 ],
                "choices": [ "Digital Audio", "Non-Audio" ],
                "desc": "Data mode"
            },
            "SCMS": {
                "bits": [ 5 ],
                "choices": [ "Copy Restricted", "Copy Permitted" ],
                "desc": "Copy protection"
            },
            "PREEMPHASIS": {
                "bits": [ 4, 3, 2 ],
                "choices": [ "None - 2ch", "50/10us - 2ch", "Reserved - 2 ch", "Reserved - 2ch", "Reserved - 4ch", "Reserved - 4ch", "Reserved - 4ch", "Reserved - 4ch" ],
                "desc": "Pre-emphasis"
            },
        }
    },
    {   "name": "0x02",     # DIR Channel Status Ch1 Byte 1
        "regs": [ 0x02 ],
        "desc": "DIR Channel Status Ch1 Byte 1",
        "fields": {
            "CATEGORY": {
                "bits": [ 7, 6, 5, 4, 3, 2, 1 ],
                "choices": [
                            "General",
                            "CD - compatible with IEC908",
                            "PCM encoder / decoder",
                            "DAT",
                            "Broadcast Digital Audio - Japan",
                            "Synthesiser",
                            "A/D converter without SCMS",
                            "Reserved",
                            "Solid state memory",
                            "CD - Incompatible with IEC908",
                            "Digital / digital converter",
                            "Digital audio sound VCR",
                            "Broadcast Digital Audio - Europe",
                            "Synthesiser",
                            "Broadcast digital audio",
                            "Reserved",
                            "Reserved",
                            "Laser optical",
                            "Digital signal mixer",
                            "Magnetic tape or disc",
                            "Broadcast Digital Audio",
                            "Musical Instrument",
                            "A/D converter with SCMS",
                            "Reserved",
                            "Solid state memory",
                            "Laser optical",
                            "Sample rate converter",
                            "Magnetic tape or disc",
                            "Broadcast Digital Audio",
                            "Musical Instrument",
                            "Broadcast digital audio",
                            "Reserved",
                            "Reserved",
                            "Laser optical",
                            "Digital sound sampler",
                            "Magnetic tape or disc",
                            "Broadcast Digital Audio",
                            "Musical Instrument",
                            "A/D converter without SCMS",
                            "Reserved",
                            "Solid state memory",
                            "Laser optical",
                            "Digital / digital converter",
                            "Magnetic tape or disc",
                            "Broadcast Digital Audio",
                            "Musical Instrument",
                            "Broadcast digital audio",
                            "Reserved",
                            "Reserved",
                            "Laser optical",
                            "Digital / digital converter",
                            "Magnetic tape or disc",
                            "Broadcast Digital Audio",
                            "Musical Instrument",
                            "A/D converter with SCMS",
                            "Reserved",
                            "Solid state memory",
                            "Laser optical",
                            "Digital / digital converter",
                            "Magnetic tape or disc",
                            "Broadcast Digital Audio",
                            "Musical Instrument",
                            "Broadcast digital audio",
                            "Reserved",
                            "Experimental",
                            "Laser optical",
                            "Digital / digital converter",
                            "DCC",
                            "Broadcast Digital Audio - Electronic software delivery",
                            "Musical Instrument",
                            "A/D converter without SCMS",
                            "Reserved",
                            "Solid state memory",
                            "MiniDisc",
                            "Digital / digital converter",
                            "Magnetic tape or disc",
                            "Broadcast Digital Audio",
                            "Musical Instrument",
                            "Broadcast digital audio",
                            "Reserved",
                            "Reserved",
                            "Laser optical",
                            "Digital / digital converter",
                            "Magnetic tape or disc",
                            "Broadcast Digital Audio",
                            "Musical Instrument",
                            "A/D converter with SCMS",
                            "Reserved",
                            "Solid state memory",
                            "Laser optical",
                            "Digital / digital converter",
                            "Magnetic tape or disc",
                            "Broadcast Digital Audio",
                            "Musical Instrument",
                            "Broadcast digital audio",
                            "Reserved",
                            "Reserved",
                            "Laser optical",
                            "Digital / digital converter",
                            "Magnetic tape or disc",
                            "Broadcast Digital Audio - United States",
                            "Musical Instrument",
                            "A/D converter without SCMS",
                            "Reserved",
                            "Solid state memory",
                            "Laser optical",
                            "Digital / digital converter",
                            "Magnetic tape or disc",
                            "Broadcast Digital Audio",
                            "Musical Instrument",
                            "Broadcast digital audio",
                            "Reserved",
                            "Reserved",
                            "Laser optical",
                            "Digital / digital converter",
                            "Magnetic tape or disc",
                            "Broadcast Digital Audio",
                            "Musical Instrument",
                            "A/D converter with SCMS",
                            "Reserved",
                            "Solid state memory",
                            "Laser optical",
                            "Digital / digital converter",
                            "Magnetic tape or disc",
                            "Broadcast Digital Audio",
                            "Musical Instrument",
                            "Broadcast digital audio",
                            "Reserved",
                           ],
                "desc": "Category Code"
            },
            "L": {
                "bits": [ 0 ],
                "choices": [ "Original", "1st gen or higher" ],
                "desc": "Generation"
            },
        }
    },
    {   "name": "0x03",     # DIR Channel Status Ch2 Byte 1
        "regs": [ 0x03 ],
        "desc": "DIR Channel Status Ch2 Byte 1",
        "fields": {
            "CATEGORY": {
                "bits": [ 7, 6, 5, 4, 3, 2, 1 ],
                "choices": [
                            "General",
                            "CD - compatible with IEC908",
                            "PCM encoder / decoder",
                            "DAT",
                            "Broadcast Digital Audio - Japan",
                            "Synthesiser",
                            "A/D converter without SCMS",
                            "Reserved",
                            "Solid state memory",
                            "CD - Incompatible with IEC908",
                            "Digital / digital converter",
                            "Digital audio sound VCR",
                            "Broadcast Digital Audio - Europe",
                            "Synthesiser",
                            "Broadcast digital audio",
                            "Reserved",
                            "Reserved",
                            "Laser optical",
                            "Digital signal mixer",
                            "Magnetic tape or disc",
                            "Broadcast Digital Audio",
                            "Musical Instrument",
                            "A/D converter with SCMS",
                            "Reserved",
                            "Solid state memory",
                            "Laser optical",
                            "Sample rate converter",
                            "Magnetic tape or disc",
                            "Broadcast Digital Audio",
                            "Musical Instrument",
                            "Broadcast digital audio",
                            "Reserved",
                            "Reserved",
                            "Laser optical",
                            "Digital sound sampler",
                            "Magnetic tape or disc",
                            "Broadcast Digital Audio",
                            "Musical Instrument",
                            "A/D converter without SCMS",
                            "Reserved",
                            "Solid state memory",
                            "Laser optical",
                            "Digital / digital converter",
                            "Magnetic tape or disc",
                            "Broadcast Digital Audio",
                            "Musical Instrument",
                            "Broadcast digital audio",
                            "Reserved",
                            "Reserved",
                            "Laser optical",
                            "Digital / digital converter",
                            "Magnetic tape or disc",
                            "Broadcast Digital Audio",
                            "Musical Instrument",
                            "A/D converter with SCMS",
                            "Reserved",
                            "Solid state memory",
                            "Laser optical",
                            "Digital / digital converter",
                            "Magnetic tape or disc",
                            "Broadcast Digital Audio",
                            "Musical Instrument",
                            "Broadcast digital audio",
                            "Reserved",
                            "Experimental",
                            "Laser optical",
                            "Digital / digital converter",
                            "DCC",
                            "Broadcast Digital Audio - Electronic software delivery",
                            "Musical Instrument",
                            "A/D converter without SCMS",
                            "Reserved",
                            "Solid state memory",
                            "MiniDisc",
                            "Digital / digital converter",
                            "Magnetic tape or disc",
                            "Broadcast Digital Audio",
                            "Musical Instrument",
                            "Broadcast digital audio",
                            "Reserved",
                            "Reserved",
                            "Laser optical",
                            "Digital / digital converter",
                            "Magnetic tape or disc",
                            "Broadcast Digital Audio",
                            "Musical Instrument",
                            "A/D converter with SCMS",
                            "Reserved",
                            "Solid state memory",
                            "Laser optical",
                            "Digital / digital converter",
                            "Magnetic tape or disc",
                            "Broadcast Digital Audio",
                            "Musical Instrument",
                            "Broadcast digital audio",
                            "Reserved",
                            "Reserved",
                            "Laser optical",
                            "Digital / digital converter",
                            "Magnetic tape or disc",
                            "Broadcast Digital Audio - United States",
                            "Musical Instrument",
                            "A/D converter without SCMS",
                            "Reserved",
                            "Solid state memory",
                            "Laser optical",
                            "Digital / digital converter",
                            "Magnetic tape or disc",
                            "Broadcast Digital Audio",
                            "Musical Instrument",
                            "Broadcast digital audio",
                            "Reserved",
                            "Reserved",
                            "Laser optical",
                            "Digital / digital converter",
                            "Magnetic tape or disc",
                            "Broadcast Digital Audio",
                            "Musical Instrument",
                            "A/D converter with SCMS",
                            "Reserved",
                            "Solid state memory",
                            "Laser optical",
                            "Digital / digital converter",
                            "Magnetic tape or disc",
                            "Broadcast Digital Audio",
                            "Musical Instrument",
                            "Broadcast digital audio",
                            "Reserved",
                           ],
                "desc": "Category Code"
            },
            "L": {
                "bits": [ 0 ],
                "choices": [ "Original", "1st gen or higher" ],
                "desc": "Generation"
            },
        }
    },
    {   "name": "0x04",     # DIR Channel Status Ch1 Byte 2
        "regs": [ 0x04 ],  # low to high
        "desc": "DIR Channel Status Ch2 Byte 2",
        "fields": {
            "SOURCE": {
                "bits": [ 7, 6, 5, 4 ],
                "choices": [ "Unspecified", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13", "14", "15" ],
                "desc": "Source"
            },
            "CHANNEL": {
                "bits": [ 3, 2, 1, 0 ],
                "choices": [ "Unspecified", "A (Left)", "B (Right)", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O" ],
                "desc": "Channel"
            },
        }
    },
    {   "name": "0x05",     # DIR Channel Status Ch2 Byte 2
        "regs": [ 0x05 ],  # low to high
        "desc": "DIR Channel Status Ch2 Byte 2",
        "fields": {
            "SOURCE": {
                "bits": [ 7, 6, 5, 4 ],
                "choices": [ "Unspecified", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13", "14", "15" ],
                "desc": "Source"
            },
            "CHANNEL": {
                "bits": [ 3, 2, 1, 0 ],
                "choices": [ "Unspecified", "A (Left)", "B (Right)", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O" ],
                "desc": "Channel"
            },
        }
    },
    {   "name": "0x06",     # DIR Channel Status Ch1 Byte 3
        "regs": [ 0x06 ],  # low to high
        "desc": "DIR Channel Status Ch2 Byte 3",
        "fields": {
            "FREQ": {
                "bits": [ 7, 6, 5, 4 ],
                "choices": [ "44.1kHz", "Reserved", "48kHz", "32kHz", "22.05kHz", "Reserved", "24kHz", "Reserved", "88.2kHz", "Reserved", "96kHz", "Reserved", "176.4kHz", "Reserved", "192kHz", "Reserved" ],
                "desc": "Sample Frequency (Fs)"
            },
            "ACCURACY": {
                "bits": [ 3, 2 ],
                "choices": [ "Level 2", "Level 1", "Level 3", "Reserved" ],
                "desc": "Clock accuracy"
            },
        }
    },
    {   "name": "0x07",     # DIR Channel Status Ch2 Byte 3
        "regs": [ 0x07 ],  # low to high
        "desc": "DIR Channel Status Ch2 Byte 3",
        "fields": {
            "FREQ": {
                "bits": [ 7, 6, 5, 4 ],
                "choices": [ "44.1kHz", "Reserved", "48kHz", "32kHz", "22.05kHz", "Reserved", "24kHz", "Reserved", "88.2kHz", "Reserved", "96kHz", "Reserved", "176.4kHz", "Reserved", "192kHz", "Reserved" ],
                "desc": "Sample Frequency (Fs)"
            },
            "ACCURACY": {
                "bits": [ 3, 2 ],
                "choices": [ "Level 2", "Level 1", "Level 3", "Reserved" ],
                "desc": "Clock accuracy"
            },
        }
    },
    {   "name": "0x08",     # DIR Channel Status Ch1 Byte 4
        "regs": [ 0x08 ],  # low to high
        "desc": "DIR Channel Status Ch1 Byte 4",
    },
    {   "name": "0x09",     # DIR Channel Status Ch2 Byte 4
        "regs": [ 0x09 ],  # low to high
        "desc": "DIR Channel Status Ch2 Byte 4",
    },
    {   "name": "0x0A",     # DIR Channel Status Ch1 Byte 5
        "regs": [ 0x0A ],  # low to high
        "desc": "DIR Channel Status Ch1 Byte 5",
    },
    {   "name": "0x0B",     # DIR Channel Status Ch2 Byte 5
        "regs": [ 0x0B ],  # low to high
        "desc": "DIR Channel Status Ch2 Byte 5",
    },
    {   "name": "0x0C",     # DIR Channel Status Ch1 Byte 6
        "regs": [ 0x0C ],  # low to high
        "desc": "DIR Channel Status Ch1 Byte 6",
    },
    {   "name": "0x0D",     # DIR Channel Status Ch2 Byte 6
        "regs": [ 0x0D ],  # low to high
        "desc": "DIR Channel Status Ch2 Byte 6",
    },
    {   "name": "0x0E",     # DIR Channel Status Ch1 Byte 7
        "regs": [ 0x0E ],  # low to high
        "desc": "DIR Channel Status Ch1 Byte 7",
    },
    {   "name": "0x0F",     # DIR Channel Status Ch2 Byte 7
        "regs": [ 0x0F ],  # low to high
        "desc": "DIR Channel Status Ch2 Byte 7",
    },
    {   "name": "0x10",     # DIR Channel Status Ch1 Byte 8
        "regs": [ 0x10 ],  # low to high
        "desc": "DIR Channel Status Ch1 Byte 8",
    },
    {   "name": "0x11",     # DIR Channel Status Ch2 Byte 8
        "regs": [ 0x11 ],  # low to high
        "desc": "DIR Channel Status Ch2 Byte 8",
    },
    {   "name": "0x12",     # DIR Channel Status Ch1 Byte 9
        "regs": [ 0x12 ],  # low to high
        "desc": "DIR Channel Status Ch1 Byte 9",
    },
    {   "name": "0x13",     # DIR Channel Status Ch2 Byte 9
        "regs": [ 0x13 ],  # low to high
        "desc": "DIR Channel Status Ch2 Byte 9",
    },
    {   "name": "0x14",     # DIR Channel Status Ch1 Byte 10
        "regs": [ 0x14 ],  # low to high
        "desc": "DIR Channel Status Ch1 Byte 10",
    },
    {   "name": "0x15",     # DIR Channel Status Ch2 Byte 10
        "regs": [ 0x15 ],  # low to high
        "desc": "DIR Channel Status Ch2 Byte 10",
    },
    {   "name": "0x16",     # DIR Channel Status Ch1 Byte 11
        "regs": [ 0x16 ],  # low to high
        "desc": "DIR Channel Status Ch1 Byte 11",
    },
    {   "name": "0x17",     # DIR Channel Status Ch2 Byte 11
        "regs": [ 0x17 ],  # low to high
        "desc": "DIR Channel Status Ch2 Byte 11",
    },
    {   "name": "0x18",     # DIR Channel Status Ch1 Byte 12
        "regs": [ 0x18 ],  # low to high
        "desc": "DIR Channel Status Ch1 Byte 12",
    },
    {   "name": "0x19",     # DIR Channel Status Ch2 Byte 12
        "regs": [ 0x19 ],  # low to high
        "desc": "DIR Channel Status Ch2 Byte 12",
    },
    {   "name": "0x1A",     # DIR Channel Status Ch1 Byte 13
        "regs": [ 0x1A ],  # low to high
        "desc": "DIR Channel Status Ch1 Byte 13",
    },
    {   "name": "0x1B",     # DIR Channel Status Ch2 Byte 13
        "regs": [ 0x1B ],  # low to high
        "desc": "DIR Channel Status Ch2 Byte 13",
    },
    {   "name": "0x1C",     # DIR Channel Status Ch1 Byte 14
        "regs": [ 0x1C ],  # low to high
        "desc": "DIR Channel Status Ch1 Byte 14",
    },
    {   "name": "0x1D",     # DIR Channel Status Ch2 Byte 14
        "regs": [ 0x1D ],  # low to high
        "desc": "DIR Channel Status Ch2 Byte 14",
    },
    {   "name": "0x1E",     # DIR Channel Status Ch1 Byte 15
        "regs": [ 0x1E ],  # low to high
        "desc": "DIR Channel Status Ch1 Byte 15",
    },
    {   "name": "0x1F",     # DIR Channel Status Ch2 Byte 15
        "regs": [ 0x1F ],  # low to high
        "desc": "DIR Channel Status Ch2 Byte 15",
    },
    {   "name": "0x20",     # DIR Channel Status Ch1 Byte 16
        "regs": [ 0x20 ],  # low to high
        "desc": "DIR Channel Status Ch1 Byte 16",
    },
    {   "name": "0x21",     # DIR Channel Status Ch2 Byte 16
        "regs": [ 0x21 ],  # low to high
        "desc": "DIR Channel Status Ch2 Byte 16",
    },
    {   "name": "0x22",     # DIR Channel Status Ch1 Byte 17
        "regs": [ 0x22 ],  # low to high
        "desc": "DIR Channel Status Ch1 Byte 17",
    },
    {   "name": "0x23",     # DIR Channel Status Ch2 Byte 17
        "regs": [ 0x23 ],  # low to high
        "desc": "DIR Channel Status Ch2 Byte 17",
    },
    {   "name": "0x24",     # DIR Channel Status Ch1 Byte 18
        "regs": [ 0x24 ],  # low to high
        "desc": "DIR Channel Status Ch1 Byte 18",
    },
    {   "name": "0x25",     # DIR Channel Status Ch2 Byte 18
        "regs": [ 0x25 ],  # low to high
        "desc": "DIR Channel Status Ch2 Byte 18",
    },
    {   "name": "0x26",     # DIR Channel Status Ch1 Byte 19
        "regs": [ 0x26 ],  # low to high
        "desc": "DIR Channel Status Ch1 Byte 19",
    },
    {   "name": "0x27",     # DIR Channel Status Ch2 Byte 19
        "regs": [ 0x27 ],  # low to high
        "desc": "DIR Channel Status Ch2 Byte 19",
    },
    {   "name": "0x28",     # DIR Channel Status Ch1 Byte 20
        "regs": [ 0x28 ],  # low to high
        "desc": "DIR Channel Status Ch1 Byte 20",
    },
    {   "name": "0x29",     # DIR Channel Status Ch2 Byte 20
        "regs": [ 0x29 ],  # low to high
        "desc": "DIR Channel Status Ch2 Byte 20",
    },
    {   "name": "0x2A",     # DIR Channel Status Ch1 Byte 21
        "regs": [ 0x2A ],  # low to high
        "desc": "DIR Channel Status Ch1 Byte 21",
    },
    {   "name": "0x2B",     # DIR Channel Status Ch2 Byte 21
        "regs": [ 0x2B ],  # low to high
        "desc": "DIR Channel Status Ch2 Byte 21",
    },
    {   "name": "0x2C",     # DIR Channel Status Ch1 Byte 22
        "regs": [ 0x2C ],  # low to high
        "desc": "DIR Channel Status Ch1 Byte 22",
    },
    {   "name": "0x2D",     # DIR Channel Status Ch2 Byte 22
        "regs": [ 0x2D ],  # low to high
        "desc": "DIR Channel Status Ch2 Byte 22",
    },
    {   "name": "0x2E",     # DIR Channel Status Ch1 Byte 33
        "regs": [ 0x2E ],  # low to high
        "desc": "DIR Channel Status Ch1 Byte 23",
    },
    {   "name": "0x2F",     # DIR Channel Status Ch2 Byte 33
        "regs": [ 0x2F ],  # low to high
        "desc": "DIR Channel Status Ch2 Byte 23",
    },
    {   "name": "0x40",     # DIR User Data Ch1 Byte 0
        "regs": [ 0x40 ],  # low to high
        "desc": "DIR User Data Ch1 Byte 0",
    },
    {   "name": "0x41",     # DIR User Data Ch2 Byte 0
        "regs": [ 0x41 ],  # low to high
        "desc": "DIR User Data Ch2 Byte 0",
    },
    {   "name": "0x42",     # DIR User Data Ch1 Byte 1
        "regs": [ 0x42 ],  # low to high
        "desc": "DIR User Data Ch1 Byte 1",
    },
    {   "name": "0x43",     # DIR User Data Ch2 Byte 1
        "regs": [ 0x43 ],  # low to high
        "desc": "DIR User Data Ch2 Byte 1",
    },
    {   "name": "0x44",     # DIR User Data Ch1 Byte 2
        "regs": [ 0x44 ],  # low to high
        "desc": "DIR User Data Ch1 Byte 2",
    },
    {   "name": "0x45",     # DIR User Data Ch2 Byte 2
        "regs": [ 0x45 ],  # low to high
        "desc": "DIR User Data Ch2 Byte 2",
    },
    {   "name": "0x46",     # DIR User Data Ch1 Byte 3
        "regs": [ 0x46 ],  # low to high
        "desc": "DIR User Data Ch1 Byte 3",
    },
    {   "name": "0x47",     # DIR User Data Ch2 Byte 3
        "regs": [ 0x47 ],  # low to high
        "desc": "DIR User Data Ch2 Byte 3",
    },
    {   "name": "0x48",     # DIR User Data Ch1 Byte 4
        "regs": [ 0x48 ],  # low to high
        "desc": "DIR User Data Ch1 Byte 4",
    },
    {   "name": "0x49",     # DIR User Data Ch2 Byte 4
        "regs": [ 0x49 ],  # low to high
        "desc": "DIR User Data Ch2 Byte 4",
    },
    {   "name": "0x4A",     # DIR User Data Ch1 Byte 5
        "regs": [ 0x4A ],  # low to high
        "desc": "DIR User Data Ch1 Byte 5",
    },
    {   "name": "0x4B",     # DIR User Data Ch2 Byte 5
        "regs": [ 0x4B ],  # low to high
        "desc": "DIR User Data Ch2 Byte 5",
    },
    {   "name": "0x4C",     # DIR User Data Ch1 Byte 6
        "regs": [ 0x4C ],  # low to high
        "desc": "DIR User Data Ch1 Byte 6",
    },
    {   "name": "0x4D",     # DIR User Data Ch2 Byte 6
        "regs": [ 0x4D ],  # low to high
        "desc": "DIR User Data Ch2 Byte 6",
    },
    {   "name": "0x4E",     # DIR User Data Ch1 Byte 7
        "regs": [ 0x4E ],  # low to high
        "desc": "DIR User Data Ch1 Byte 7",
    },
    {   "name": "0x4F",     # DIR User Data Ch2 Byte 7
        "regs": [ 0x4F ],  # low to high
        "desc": "DIR User Data Ch2 Byte 7",
    },
    {   "name": "0x50",     # DIR User Data Ch1 Byte 8
        "regs": [ 0x50 ],  # low to high
        "desc": "DIR User Data Ch1 Byte 8",
    },
    {   "name": "0x51",     # DIR User Data Ch2 Byte 8
        "regs": [ 0x51 ],  # low to high
        "desc": "DIR User Data Ch2 Byte 8",
    },
    {   "name": "0x52",     # DIR User Data Ch1 Byte 9
        "regs": [ 0x52 ],  # low to high
        "desc": "DIR User Data Ch1 Byte 9",
    },
    {   "name": "0x53",     # DIR User Data Ch2 Byte 9
        "regs": [ 0x53 ],  # low to high
        "desc": "DIR User Data Ch2 Byte 9",
    },
    {   "name": "0x54",     # DIR User Data Ch1 Byte 10
        "regs": [ 0x54 ],  # low to high
        "desc": "DIR User Data Ch1 Byte 10",
    },
    {   "name": "0x55",     # DIR User Data Ch2 Byte 10
        "regs": [ 0x55 ],  # low to high
        "desc": "DIR User Data Ch2 Byte 10",
    },
    {   "name": "0x56",     # DIR User Data Ch1 Byte 11
        "regs": [ 0x56 ],  # low to high
        "desc": "DIR User Data Ch1 Byte 11",
    },
    {   "name": "0x57",     # DIR User Data Ch2 Byte 11
        "regs": [ 0x57 ],  # low to high
        "desc": "DIR User Data Ch2 Byte 11",
    },
    {   "name": "0x58",     # DIR User Data Ch1 Byte 12
        "regs": [ 0x58 ],  # low to high
        "desc": "DIR User Data Ch1 Byte 12",
    },
    {   "name": "0x59",     # DIR User Data Ch2 Byte 12
        "regs": [ 0x59 ],  # low to high
        "desc": "DIR User Data Ch2 Byte 12",
    },
    {   "name": "0x5A",     # DIR User Data Ch1 Byte 13
        "regs": [ 0x5A ],  # low to high
        "desc": "DIR User Data Ch1 Byte 13",
    },
    {   "name": "0x5B",     # DIR User Data Ch2 Byte 13
        "regs": [ 0x5B ],  # low to high
        "desc": "DIR User Data Ch2 Byte 13",
    },
    {   "name": "0x5C",     # DIR User Data Ch1 Byte 14
        "regs": [ 0x5C ],  # low to high
        "desc": "DIR User Data Ch1 Byte 14",
    },
    {   "name": "0x5D",     # DIR User Data Ch2 Byte 14
        "regs": [ 0x5D ],  # low to high
        "desc": "DIR User Data Ch2 Byte 14",
    },
    {   "name": "0x5E",     # DIR User Data Ch1 Byte 15
        "regs": [ 0x5E ],  # low to high
        "desc": "DIR User Data Ch1 Byte 15",
    },
    {   "name": "0x5F",     # DIR User Data Ch2 Byte 15
        "regs": [ 0x5F ],  # low to high
        "desc": "DIR User Data Ch2 Byte 15",
    },
    {   "name": "0x60",     # DIR User Data Ch1 Byte 16
        "regs": [ 0x60 ],  # low to high
        "desc": "DIR User Data Ch1 Byte 16",
    },
    {   "name": "0x61",     # DIR User Data Ch2 Byte 16
        "regs": [ 0x61 ],  # low to high
        "desc": "DIR User Data Ch2 Byte 16",
    },
    {   "name": "0x62",     # DIR User Data Ch1 Byte 17
        "regs": [ 0x62 ],  # low to high
        "desc": "DIR User Data Ch1 Byte 17",
    },
    {   "name": "0x63",     # DIR User Data Ch2 Byte 17
        "regs": [ 0x63 ],  # low to high
        "desc": "DIR User Data Ch2 Byte 17",
    },
    {   "name": "0x64",     # DIR User Data Ch1 Byte 18
        "regs": [ 0x64 ],  # low to high
        "desc": "DIR User Data Ch1 Byte 18",
    },
    {   "name": "0x65",     # DIR User Data Ch2 Byte 18
        "regs": [ 0x65 ],  # low to high
        "desc": "DIR User Data Ch2 Byte 18",
    },
    {   "name": "0x66",     # DIR User Data Ch1 Byte 19
        "regs": [ 0x66 ],  # low to high
        "desc": "DIR User Data Ch1 Byte 19",
    },
    {   "name": "0x67",     # DIR User Data Ch1 Byte 19
        "regs": [ 0x67 ],  # low to high
        "desc": "DIR User Data Ch2 Byte 19",
    },
    {   "name": "0x68",     # DIR User Data Ch2 Byte 20
        "regs": [ 0x68 ],  # low to high
        "desc": "DIR User Data Ch1 Byte 20",
    },
    {   "name": "0x69",     # DIR User Data Ch1 Byte 20
        "regs": [ 0x69 ],  # low to high
        "desc": "DIR User Data Ch2 Byte 20",
    },
    {   "name": "0x6A",     # DIR User Data Ch2 Byte 21
        "regs": [ 0x6A ],  # low to high
        "desc": "DIR User Data Ch1 Byte 21",
    },
    {   "name": "0x6B",     # DIR User Data Ch1 Byte 21
        "regs": [ 0x6B ],  # low to high
        "desc": "DIR User Data Ch2 Byte 21",
    },
    {   "name": "0x6C",     # DIR User Data Ch2 Byte 22
        "regs": [ 0x6C ],  # low to high
        "desc": "DIR User Data Ch1 Byte 22",
    },
    {   "name": "0x6D",     # DIR User Data Ch1 Byte 22
        "regs": [ 0x6D ],  # low to high
        "desc": "DIR User Data Ch2 Byte 22",
    },
    {   "name": "0x6E",     # DIR User Data Ch2 Byte 23
        "regs": [ 0x6E ],  # low to high
        "desc": "DIR User Data Ch1 Byte 23",
    },
    {   "name": "0x6F",     # DIR User Data Ch1 Byte 23
        "regs": [ 0x6F ],  # low to high
        "desc": "DIR User Data Ch2 Byte 23",
    },
)

src4392_page2 = (
    {   "name": "0x00",     # DIT Channel Status Ch1 Byte 0
        "regs": [ 0x00 ],
        "desc": "DIT Channel Status Ch1 Byte 0",
        "fields": {
            "FORMAT": {
                "bits": [ 7 ],
                "choices": [ "S/PDIF", "AES3" ],
                "desc": "Data format"
            },
            "MODE": {
                "bits": [ 6 ],
                "choices": [ "Digital Audio", "Non-Audio" ],
                "desc": "Data mode"
            },
            "SCMS": {
                "bits": [ 5 ],
                "choices": [ "Copy Restricted", "Copy Permitted" ],
                "desc": "Copy protection"
            },
            "PREEMPHASIS": {
                "bits": [ 4, 3, 2 ],
                "choices": [ "None - 2ch", "50/10us - 2ch", "Reserved - 2 ch", "Reserved - 2ch", "Reserved - 4ch", "Reserved - 4ch", "Reserved - 4ch", "Reserved - 4ch" ],
                "desc": "Pre-emphasis"
            },
        }
    },
    {   "name": "0x01",     # DIT Channel Status Ch2 Byte 0
        "regs": [ 0x01 ],
        "desc": "DIT Channel Status Ch2 Byte 0",
        "fields": {
            "FORMAT": {
                "bits": [ 7 ],
                "choices": [ "S/PDIF", "AES3" ],
                "desc": "Data format"
            },
            "MODE": {
                "bits": [ 6 ],
                "choices": [ "Digital Audio", "Non-Audio" ],
                "desc": "Data mode"
            },
            "SCMS": {
                "bits": [ 5 ],
                "choices": [ "Copy Restricted", "Copy Permitted" ],
                "desc": "Copy protection"
            },
            "PREEMPHASIS": {
                "bits": [ 4, 3, 2 ],
                "choices": [ "None - 2ch", "50/10us - 2ch", "Reserved - 2 ch", "Reserved - 2ch", "Reserved - 4ch", "Reserved - 4ch", "Reserved - 4ch", "Reserved - 4ch" ],
                "desc": "Pre-emphasis"
            },
        }
    },
    {   "name": "0x02",     # DIT Channel Status Ch1 Byte 1
        "regs": [ 0x02 ],
        "desc": "DIT Channel Status Ch1 Byte 1",
        "fields": {
            "CATEGORY": {
                "bits": [ 7, 6, 5, 4, 3, 2, 1 ],
                "choices": [
                            "General",
                            "CD - compatible with IEC908",
                            "PCM encoder / decoder",
                            "DAT",
                            "Broadcast Digital Audio - Japan",
                            "Synthesiser",
                            "A/D converter without SCMS",
                            "Reserved",
                            "Solid state memory",
                            "CD - Incompatible with IEC908",
                            "Digital / digital converter",
                            "Digital audio sound VCR",
                            "Broadcast Digital Audio - Europe",
                            "Synthesiser",
                            "Broadcast digital audio",
                            "Reserved",
                            "Reserved",
                            "Laser optical",
                            "Digital signal mixer",
                            "Magnetic tape or disc",
                            "Broadcast Digital Audio",
                            "Musical Instrument",
                            "A/D converter with SCMS",
                            "Reserved",
                            "Solid state memory",
                            "Laser optical",
                            "Sample rate converter",
                            "Magnetic tape or disc",
                            "Broadcast Digital Audio",
                            "Musical Instrument",
                            "Broadcast digital audio",
                            "Reserved",
                            "Reserved",
                            "Laser optical",
                            "Digital sound sampler",
                            "Magnetic tape or disc",
                            "Broadcast Digital Audio",
                            "Musical Instrument",
                            "A/D converter without SCMS",
                            "Reserved",
                            "Solid state memory",
                            "Laser optical",
                            "Digital / digital converter",
                            "Magnetic tape or disc",
                            "Broadcast Digital Audio",
                            "Musical Instrument",
                            "Broadcast digital audio",
                            "Reserved",
                            "Reserved",
                            "Laser optical",
                            "Digital / digital converter",
                            "Magnetic tape or disc",
                            "Broadcast Digital Audio",
                            "Musical Instrument",
                            "A/D converter with SCMS",
                            "Reserved",
                            "Solid state memory",
                            "Laser optical",
                            "Digital / digital converter",
                            "Magnetic tape or disc",
                            "Broadcast Digital Audio",
                            "Musical Instrument",
                            "Broadcast digital audio",
                            "Reserved",
                            "Experimental",
                            "Laser optical",
                            "Digital / digital converter",
                            "DCC",
                            "Broadcast Digital Audio - Electronic software delivery",
                            "Musical Instrument",
                            "A/D converter without SCMS",
                            "Reserved",
                            "Solid state memory",
                            "MiniDisc",
                            "Digital / digital converter",
                            "Magnetic tape or disc",
                            "Broadcast Digital Audio",
                            "Musical Instrument",
                            "Broadcast digital audio",
                            "Reserved",
                            "Reserved",
                            "Laser optical",
                            "Digital / digital converter",
                            "Magnetic tape or disc",
                            "Broadcast Digital Audio",
                            "Musical Instrument",
                            "A/D converter with SCMS",
                            "Reserved",
                            "Solid state memory",
                            "Laser optical",
                            "Digital / digital converter",
                            "Magnetic tape or disc",
                            "Broadcast Digital Audio",
                            "Musical Instrument",
                            "Broadcast digital audio",
                            "Reserved",
                            "Reserved",
                            "Laser optical",
                            "Digital / digital converter",
                            "Magnetic tape or disc",
                            "Broadcast Digital Audio - United States",
                            "Musical Instrument",
                            "A/D converter without SCMS",
                            "Reserved",
                            "Solid state memory",
                            "Laser optical",
                            "Digital / digital converter",
                            "Magnetic tape or disc",
                            "Broadcast Digital Audio",
                            "Musical Instrument",
                            "Broadcast digital audio",
                            "Reserved",
                            "Reserved",
                            "Laser optical",
                            "Digital / digital converter",
                            "Magnetic tape or disc",
                            "Broadcast Digital Audio",
                            "Musical Instrument",
                            "A/D converter with SCMS",
                            "Reserved",
                            "Solid state memory",
                            "Laser optical",
                            "Digital / digital converter",
                            "Magnetic tape or disc",
                            "Broadcast Digital Audio",
                            "Musical Instrument",
                            "Broadcast digital audio",
                            "Reserved",
                           ],
                "desc": "Category Code"
            },
            "L": {
                "bits": [ 0 ],
                "choices": [ "Original", "1st gen or higher" ],
                "desc": "Generation"
            },
        }
    },
    {   "name": "0x03",     # DIT Channel Status Ch2 Byte 1
        "regs": [ 0x03 ],
        "desc": "DIT Channel Status Ch2 Byte 1",
        "fields": {
            "CATEGORY": {
                "bits": [ 7, 6, 5, 4, 3, 2, 1 ],
                "choices": [
                            "General",
                            "CD - compatible with IEC908",
                            "PCM encoder / decoder",
                            "DAT",
                            "Broadcast Digital Audio - Japan",
                            "Synthesiser",
                            "A/D converter without SCMS",
                            "Reserved",
                            "Solid state memory",
                            "CD - Incompatible with IEC908",
                            "Digital / digital converter",
                            "Digital audio sound VCR",
                            "Broadcast Digital Audio - Europe",
                            "Synthesiser",
                            "Broadcast digital audio",
                            "Reserved",
                            "Reserved",
                            "Laser optical",
                            "Digital signal mixer",
                            "Magnetic tape or disc",
                            "Broadcast Digital Audio",
                            "Musical Instrument",
                            "A/D converter with SCMS",
                            "Reserved",
                            "Solid state memory",
                            "Laser optical",
                            "Sample rate converter",
                            "Magnetic tape or disc",
                            "Broadcast Digital Audio",
                            "Musical Instrument",
                            "Broadcast digital audio",
                            "Reserved",
                            "Reserved",
                            "Laser optical",
                            "Digital sound sampler",
                            "Magnetic tape or disc",
                            "Broadcast Digital Audio",
                            "Musical Instrument",
                            "A/D converter without SCMS",
                            "Reserved",
                            "Solid state memory",
                            "Laser optical",
                            "Digital / digital converter",
                            "Magnetic tape or disc",
                            "Broadcast Digital Audio",
                            "Musical Instrument",
                            "Broadcast digital audio",
                            "Reserved",
                            "Reserved",
                            "Laser optical",
                            "Digital / digital converter",
                            "Magnetic tape or disc",
                            "Broadcast Digital Audio",
                            "Musical Instrument",
                            "A/D converter with SCMS",
                            "Reserved",
                            "Solid state memory",
                            "Laser optical",
                            "Digital / digital converter",
                            "Magnetic tape or disc",
                            "Broadcast Digital Audio",
                            "Musical Instrument",
                            "Broadcast digital audio",
                            "Reserved",
                            "Experimental",
                            "Laser optical",
                            "Digital / digital converter",
                            "DCC",
                            "Broadcast Digital Audio - Electronic software delivery",
                            "Musical Instrument",
                            "A/D converter without SCMS",
                            "Reserved",
                            "Solid state memory",
                            "MiniDisc",
                            "Digital / digital converter",
                            "Magnetic tape or disc",
                            "Broadcast Digital Audio",
                            "Musical Instrument",
                            "Broadcast digital audio",
                            "Reserved",
                            "Reserved",
                            "Laser optical",
                            "Digital / digital converter",
                            "Magnetic tape or disc",
                            "Broadcast Digital Audio",
                            "Musical Instrument",
                            "A/D converter with SCMS",
                            "Reserved",
                            "Solid state memory",
                            "Laser optical",
                            "Digital / digital converter",
                            "Magnetic tape or disc",
                            "Broadcast Digital Audio",
                            "Musical Instrument",
                            "Broadcast digital audio",
                            "Reserved",
                            "Reserved",
                            "Laser optical",
                            "Digital / digital converter",
                            "Magnetic tape or disc",
                            "Broadcast Digital Audio - United States",
                            "Musical Instrument",
                            "A/D converter without SCMS",
                            "Reserved",
                            "Solid state memory",
                            "Laser optical",
                            "Digital / digital converter",
                            "Magnetic tape or disc",
                            "Broadcast Digital Audio",
                            "Musical Instrument",
                            "Broadcast digital audio",
                            "Reserved",
                            "Reserved",
                            "Laser optical",
                            "Digital / digital converter",
                            "Magnetic tape or disc",
                            "Broadcast Digital Audio",
                            "Musical Instrument",
                            "A/D converter with SCMS",
                            "Reserved",
                            "Solid state memory",
                            "Laser optical",
                            "Digital / digital converter",
                            "Magnetic tape or disc",
                            "Broadcast Digital Audio",
                            "Musical Instrument",
                            "Broadcast digital audio",
                            "Reserved",
                           ],
                "desc": "Category Code"
            },
            "L": {
                "bits": [ 0 ],
                "choices": [ "Original", "1st gen or higher" ],
                "desc": "Generation"
            },
        }
    },
    {   "name": "0x04",     # DIT Channel Status Ch1 Byte 2
        "regs": [ 0x04 ],  # low to high
        "desc": "DIT Channel Status Ch2 Byte 2",
        "fields": {
            "SOURCE": {
                "bits": [ 7, 6, 5, 4 ],
                "choices": [ "Unspecified", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13", "14", "15" ],
                "desc": "Source"
            },
            "CHANNEL": {
                "bits": [ 3, 2, 1, 0 ],
                "choices": [ "Unspecified", "A (Left)", "B (Right)", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O" ],
                "desc": "Channel"
            },
        }
    },
    {   "name": "0x05",     # DIT Channel Status Ch2 Byte 2
        "regs": [ 0x05 ],  # low to high
        "desc": "DIT Channel Status Ch2 Byte 2",
        "fields": {
            "SOURCE": {
                "bits": [ 7, 6, 5, 4 ],
                "choices": [ "Unspecified", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13", "14", "15" ],
                "desc": "Source"
            },
            "CHANNEL": {
                "bits": [ 3, 2, 1, 0 ],
                "choices": [ "Unspecified", "A (Left)", "B (Right)", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O" ],
                "desc": "Channel"
            },
        }
    },
    {   "name": "0x06",     # DIT Channel Status Ch1 Byte 3
        "regs": [ 0x06 ],  # low to high
        "desc": "DIT Channel Status Ch2 Byte 3",
        "fields": {
            "FREQ": {
                "bits": [ 7, 6, 5, 4 ],
                "choices": [ "44.1kHz", "Reserved", "48kHz", "32kHz", "22.05kHz", "Reserved", "24kHz", "Reserved", "88.2kHz", "Reserved", "96kHz", "Reserved", "176.4kHz", "Reserved", "192kHz", "Reserved" ],
                "desc": "Sample Frequency (Fs)"
            },
            "ACCURACY": {
                "bits": [ 3, 2 ],
                "choices": [ "Level 2", "Level 1", "Level 3", "Reserved" ],
                "desc": "Clock accuracy"
            },
        }
    },
    {   "name": "0x07",     # DIT Channel Status Ch2 Byte 3
        "regs": [ 0x07 ],  # low to high
        "desc": "DIT Channel Status Ch2 Byte 3",
        "fields": {
            "FREQ": {
                "bits": [ 7, 6, 5, 4 ],
                "choices": [ "44.1kHz", "Reserved", "48kHz", "32kHz", "22.05kHz", "Reserved", "24kHz", "Reserved", "88.2kHz", "Reserved", "96kHz", "Reserved", "176.4kHz", "Reserved", "192kHz", "Reserved" ],
                "desc": "Sample Frequency (Fs)"
            },
            "ACCURACY": {
                "bits": [ 3, 2 ],
                "choices": [ "Level 2", "Level 1", "Level 3", "Reserved" ],
                "desc": "Clock accuracy"
            },
        }
    },
    {   "name": "0x08",     # DIT Channel Status Ch1 Byte 4
        "regs": [ 0x08 ],  # low to high
        "desc": "DIT Channel Status Ch1 Byte 4",
    },
    {   "name": "0x09",     # DIT Channel Status Ch2 Byte 4
        "regs": [ 0x09 ],  # low to high
        "desc": "DIT Channel Status Ch2 Byte 4",
    },
    {   "name": "0x0A",     # DIT Channel Status Ch1 Byte 5
        "regs": [ 0x0A ],  # low to high
        "desc": "DIT Channel Status Ch1 Byte 5",
    },
    {   "name": "0x0B",     # DIT Channel Status Ch2 Byte 5
        "regs": [ 0x0B ],  # low to high
        "desc": "DIT Channel Status Ch2 Byte 5",
    },
    {   "name": "0x0C",     # DIT Channel Status Ch1 Byte 6
        "regs": [ 0x0C ],  # low to high
        "desc": "DIT Channel Status Ch1 Byte 6",
    },
    {   "name": "0x0D",     # DIT Channel Status Ch2 Byte 6
        "regs": [ 0x0D ],  # low to high
        "desc": "DIT Channel Status Ch2 Byte 6",
    },
    {   "name": "0x0E",     # DIT Channel Status Ch1 Byte 7
        "regs": [ 0x0E ],  # low to high
        "desc": "DIT Channel Status Ch1 Byte 7",
    },
    {   "name": "0x0F",     # DIT Channel Status Ch2 Byte 7
        "regs": [ 0x0F ],  # low to high
        "desc": "DIT Channel Status Ch2 Byte 7",
    },
    {   "name": "0x10",     # DIT Channel Status Ch1 Byte 8
        "regs": [ 0x10 ],  # low to high
        "desc": "DIT Channel Status Ch1 Byte 8",
    },
    {   "name": "0x11",     # DIT Channel Status Ch2 Byte 8
        "regs": [ 0x11 ],  # low to high
        "desc": "DIT Channel Status Ch2 Byte 8",
    },
    {   "name": "0x12",     # DIT Channel Status Ch1 Byte 9
        "regs": [ 0x12 ],  # low to high
        "desc": "DIT Channel Status Ch1 Byte 9",
    },
    {   "name": "0x13",     # DIT Channel Status Ch2 Byte 9
        "regs": [ 0x13 ],  # low to high
        "desc": "DIT Channel Status Ch2 Byte 9",
    },
    {   "name": "0x14",     # DIT Channel Status Ch1 Byte 10
        "regs": [ 0x14 ],  # low to high
        "desc": "DIT Channel Status Ch1 Byte 10",
    },
    {   "name": "0x15",     # DIT Channel Status Ch2 Byte 10
        "regs": [ 0x15 ],  # low to high
        "desc": "DIT Channel Status Ch2 Byte 10",
    },
    {   "name": "0x16",     # DIT Channel Status Ch1 Byte 11
        "regs": [ 0x16 ],  # low to high
        "desc": "DIT Channel Status Ch1 Byte 11",
    },
    {   "name": "0x17",     # DIT Channel Status Ch2 Byte 11
        "regs": [ 0x17 ],  # low to high
        "desc": "DIT Channel Status Ch2 Byte 11",
    },
    {   "name": "0x18",     # DIT Channel Status Ch1 Byte 12
        "regs": [ 0x18 ],  # low to high
        "desc": "DIT Channel Status Ch1 Byte 12",
    },
    {   "name": "0x19",     # DIT Channel Status Ch2 Byte 12
        "regs": [ 0x19 ],  # low to high
        "desc": "DIT Channel Status Ch2 Byte 12",
    },
    {   "name": "0x1A",     # DIT Channel Status Ch1 Byte 13
        "regs": [ 0x1A ],  # low to high
        "desc": "DIT Channel Status Ch1 Byte 13",
    },
    {   "name": "0x1B",     # DIT Channel Status Ch2 Byte 13
        "regs": [ 0x1B ],  # low to high
        "desc": "DIT Channel Status Ch2 Byte 13",
    },
    {   "name": "0x1C",     # DIT Channel Status Ch1 Byte 14
        "regs": [ 0x1C ],  # low to high
        "desc": "DIT Channel Status Ch1 Byte 14",
    },
    {   "name": "0x1D",     # DIT Channel Status Ch2 Byte 14
        "regs": [ 0x1D ],  # low to high
        "desc": "DIT Channel Status Ch2 Byte 14",
    },
    {   "name": "0x1E",     # DIT Channel Status Ch1 Byte 15
        "regs": [ 0x1E ],  # low to high
        "desc": "DIT Channel Status Ch1 Byte 15",
    },
    {   "name": "0x1F",     # DIT Channel Status Ch2 Byte 15
        "regs": [ 0x1F ],  # low to high
        "desc": "DIT Channel Status Ch2 Byte 15",
    },
    {   "name": "0x20",     # DIT Channel Status Ch1 Byte 16
        "regs": [ 0x20 ],  # low to high
        "desc": "DIT Channel Status Ch1 Byte 16",
    },
    {   "name": "0x21",     # DIT Channel Status Ch2 Byte 16
        "regs": [ 0x21 ],  # low to high
        "desc": "DIT Channel Status Ch2 Byte 16",
    },
    {   "name": "0x22",     # DIT Channel Status Ch1 Byte 17
        "regs": [ 0x22 ],  # low to high
        "desc": "DIT Channel Status Ch1 Byte 17",
    },
    {   "name": "0x23",     # DIT Channel Status Ch2 Byte 17
        "regs": [ 0x23 ],  # low to high
        "desc": "DIT Channel Status Ch2 Byte 17",
    },
    {   "name": "0x24",     # DIT Channel Status Ch1 Byte 18
        "regs": [ 0x24 ],  # low to high
        "desc": "DIT Channel Status Ch1 Byte 18",
    },
    {   "name": "0x25",     # DIT Channel Status Ch2 Byte 18
        "regs": [ 0x25 ],  # low to high
        "desc": "DIT Channel Status Ch2 Byte 18",
    },
    {   "name": "0x26",     # DIT Channel Status Ch1 Byte 19
        "regs": [ 0x26 ],  # low to high
        "desc": "DIT Channel Status Ch1 Byte 19",
    },
    {   "name": "0x27",     # DIT Channel Status Ch2 Byte 19
        "regs": [ 0x27 ],  # low to high
        "desc": "DIT Channel Status Ch2 Byte 19",
    },
    {   "name": "0x28",     # DIT Channel Status Ch1 Byte 20
        "regs": [ 0x28 ],  # low to high
        "desc": "DIT Channel Status Ch1 Byte 20",
    },
    {   "name": "0x29",     # DIT Channel Status Ch2 Byte 20
        "regs": [ 0x29 ],  # low to high
        "desc": "DIT Channel Status Ch2 Byte 20",
    },
    {   "name": "0x2A",     # DIT Channel Status Ch1 Byte 21
        "regs": [ 0x2A ],  # low to high
        "desc": "DIT Channel Status Ch1 Byte 21",
    },
    {   "name": "0x2B",     # DIT Channel Status Ch2 Byte 21
        "regs": [ 0x2B ],  # low to high
        "desc": "DIT Channel Status Ch2 Byte 21",
    },
    {   "name": "0x2C",     # DIT Channel Status Ch1 Byte 22
        "regs": [ 0x2C ],  # low to high
        "desc": "DIT Channel Status Ch1 Byte 22",
    },
    {   "name": "0x2D",     # DIT Channel Status Ch2 Byte 22
        "regs": [ 0x2D ],  # low to high
        "desc": "DIT Channel Status Ch2 Byte 22",
    },
    {   "name": "0x2E",     # DIT Channel Status Ch1 Byte 33
        "regs": [ 0x2E ],  # low to high
        "desc": "DIT Channel Status Ch1 Byte 23",
    },
    {   "name": "0x2F",     # DIT Channel Status Ch2 Byte 33
        "regs": [ 0x2F ],  # low to high
        "desc": "DIT Channel Status Ch2 Byte 23",
    },
    {   "name": "0x40",     # DIT User Data Ch1 Byte 0
        "regs": [ 0x40 ],  # low to high
        "desc": "DIT User Data Ch1 Byte 0",
    },
    {   "name": "0x41",     # DIT User Data Ch2 Byte 0
        "regs": [ 0x41 ],  # low to high
        "desc": "DIT User Data Ch2 Byte 0",
    },
    {   "name": "0x42",     # DIT User Data Ch1 Byte 1
        "regs": [ 0x42 ],  # low to high
        "desc": "DIT User Data Ch1 Byte 1",
    },
    {   "name": "0x43",     # DIT User Data Ch2 Byte 1
        "regs": [ 0x43 ],  # low to high
        "desc": "DIT User Data Ch2 Byte 1",
    },
    {   "name": "0x44",     # DIT User Data Ch1 Byte 2
        "regs": [ 0x44 ],  # low to high
        "desc": "DIT User Data Ch1 Byte 2",
    },
    {   "name": "0x45",     # DIT User Data Ch2 Byte 2
        "regs": [ 0x45 ],  # low to high
        "desc": "DIT User Data Ch2 Byte 2",
    },
    {   "name": "0x46",     # DIT User Data Ch1 Byte 3
        "regs": [ 0x46 ],  # low to high
        "desc": "DIT User Data Ch1 Byte 3",
    },
    {   "name": "0x47",     # DIT User Data Ch2 Byte 3
        "regs": [ 0x47 ],  # low to high
        "desc": "DIT User Data Ch2 Byte 3",
    },
    {   "name": "0x48",     # DIT User Data Ch1 Byte 4
        "regs": [ 0x48 ],  # low to high
        "desc": "DIT User Data Ch1 Byte 4",
    },
    {   "name": "0x49",     # DIT User Data Ch2 Byte 4
        "regs": [ 0x49 ],  # low to high
        "desc": "DIT User Data Ch2 Byte 4",
    },
    {   "name": "0x4A",     # DIT User Data Ch1 Byte 5
        "regs": [ 0x4A ],  # low to high
        "desc": "DIT User Data Ch1 Byte 5",
    },
    {   "name": "0x4B",     # DIT User Data Ch2 Byte 5
        "regs": [ 0x4B ],  # low to high
        "desc": "DIT User Data Ch2 Byte 5",
    },
    {   "name": "0x4C",     # DIT User Data Ch1 Byte 6
        "regs": [ 0x4C ],  # low to high
        "desc": "DIT User Data Ch1 Byte 6",
    },
    {   "name": "0x4D",     # DIT User Data Ch2 Byte 6
        "regs": [ 0x4D ],  # low to high
        "desc": "DIT User Data Ch2 Byte 6",
    },
    {   "name": "0x4E",     # DIT User Data Ch1 Byte 7
        "regs": [ 0x4E ],  # low to high
        "desc": "DIT User Data Ch1 Byte 7",
    },
    {   "name": "0x4F",     # DIT User Data Ch2 Byte 7
        "regs": [ 0x4F ],  # low to high
        "desc": "DIT User Data Ch2 Byte 7",
    },
    {   "name": "0x50",     # DIT User Data Ch1 Byte 8
        "regs": [ 0x50 ],  # low to high
        "desc": "DIT User Data Ch1 Byte 8",
    },
    {   "name": "0x51",     # DIT User Data Ch2 Byte 8
        "regs": [ 0x51 ],  # low to high
        "desc": "DIT User Data Ch2 Byte 8",
    },
    {   "name": "0x52",     # DIT User Data Ch1 Byte 9
        "regs": [ 0x52 ],  # low to high
        "desc": "DIT User Data Ch1 Byte 9",
    },
    {   "name": "0x53",     # DIT User Data Ch2 Byte 9
        "regs": [ 0x53 ],  # low to high
        "desc": "DIT User Data Ch2 Byte 9",
    },
    {   "name": "0x54",     # DIT User Data Ch1 Byte 10
        "regs": [ 0x54 ],  # low to high
        "desc": "DIT User Data Ch1 Byte 10",
    },
    {   "name": "0x55",     # DIT User Data Ch2 Byte 10
        "regs": [ 0x55 ],  # low to high
        "desc": "DIT User Data Ch2 Byte 10",
    },
    {   "name": "0x56",     # DIT User Data Ch1 Byte 11
        "regs": [ 0x56 ],  # low to high
        "desc": "DIT User Data Ch1 Byte 11",
    },
    {   "name": "0x57",     # DIT User Data Ch2 Byte 11
        "regs": [ 0x57 ],  # low to high
        "desc": "DIT User Data Ch2 Byte 11",
    },
    {   "name": "0x58",     # DIT User Data Ch1 Byte 12
        "regs": [ 0x58 ],  # low to high
        "desc": "DIT User Data Ch1 Byte 12",
    },
    {   "name": "0x59",     # DIT User Data Ch2 Byte 12
        "regs": [ 0x59 ],  # low to high
        "desc": "DIT User Data Ch2 Byte 12",
    },
    {   "name": "0x5A",     # DIT User Data Ch1 Byte 13
        "regs": [ 0x5A ],  # low to high
        "desc": "DIT User Data Ch1 Byte 13",
    },
    {   "name": "0x5B",     # DIT User Data Ch2 Byte 13
        "regs": [ 0x5B ],  # low to high
        "desc": "DIT User Data Ch2 Byte 13",
    },
    {   "name": "0x5C",     # DIT User Data Ch1 Byte 14
        "regs": [ 0x5C ],  # low to high
        "desc": "DIT User Data Ch1 Byte 14",
    },
    {   "name": "0x5D",     # DIT User Data Ch2 Byte 14
        "regs": [ 0x5D ],  # low to high
        "desc": "DIT User Data Ch2 Byte 14",
    },
    {   "name": "0x5E",     # DIT User Data Ch1 Byte 15
        "regs": [ 0x5E ],  # low to high
        "desc": "DIT User Data Ch1 Byte 15",
    },
    {   "name": "0x5F",     # DIT User Data Ch2 Byte 15
        "regs": [ 0x5F ],  # low to high
        "desc": "DIT User Data Ch2 Byte 15",
    },
    {   "name": "0x60",     # DIT User Data Ch1 Byte 16
        "regs": [ 0x60 ],  # low to high
        "desc": "DIT User Data Ch1 Byte 16",
    },
    {   "name": "0x61",     # DIT User Data Ch2 Byte 16
        "regs": [ 0x61 ],  # low to high
        "desc": "DIT User Data Ch2 Byte 16",
    },
    {   "name": "0x62",     # DIT User Data Ch1 Byte 17
        "regs": [ 0x62 ],  # low to high
        "desc": "DIT User Data Ch1 Byte 17",
    },
    {   "name": "0x63",     # DIT User Data Ch2 Byte 17
        "regs": [ 0x63 ],  # low to high
        "desc": "DIT User Data Ch2 Byte 17",
    },
    {   "name": "0x64",     # DIT User Data Ch1 Byte 18
        "regs": [ 0x64 ],  # low to high
        "desc": "DIT User Data Ch1 Byte 18",
    },
    {   "name": "0x65",     # DIT User Data Ch2 Byte 18
        "regs": [ 0x65 ],  # low to high
        "desc": "DIT User Data Ch2 Byte 18",
    },
    {   "name": "0x66",     # DIT User Data Ch1 Byte 19
        "regs": [ 0x66 ],  # low to high
        "desc": "DIT User Data Ch1 Byte 19",
    },
    {   "name": "0x67",     # DIT User Data Ch1 Byte 19
        "regs": [ 0x67 ],  # low to high
        "desc": "DIT User Data Ch2 Byte 19",
    },
    {   "name": "0x68",     # DIT User Data Ch2 Byte 20
        "regs": [ 0x68 ],  # low to high
        "desc": "DIT User Data Ch1 Byte 20",
    },
    {   "name": "0x69",     # DIT User Data Ch1 Byte 20
        "regs": [ 0x69 ],  # low to high
        "desc": "DIT User Data Ch2 Byte 20",
    },
    {   "name": "0x6A",     # DIT User Data Ch2 Byte 21
        "regs": [ 0x6A ],  # low to high
        "desc": "DIT User Data Ch1 Byte 21",
    },
    {   "name": "0x6B",     # DIT User Data Ch1 Byte 21
        "regs": [ 0x6B ],  # low to high
        "desc": "DIT User Data Ch2 Byte 21",
    },
    {   "name": "0x6C",     # DIT User Data Ch2 Byte 22
        "regs": [ 0x6C ],  # low to high
        "desc": "DIT User Data Ch1 Byte 22",
    },
    {   "name": "0x6D",     # DIT User Data Ch1 Byte 22
        "regs": [ 0x6D ],  # low to high
        "desc": "DIT User Data Ch2 Byte 22",
    },
    {   "name": "0x6E",     # DIT User Data Ch2 Byte 23
        "regs": [ 0x6E ],  # low to high
        "desc": "DIT User Data Ch1 Byte 23",
    },
    {   "name": "0x6F",     # DIT User Data Ch1 Byte 23
        "regs": [ 0x6F ],  # low to high
        "desc": "DIT User Data Ch2 Byte 23",
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
    
if len(sys.argv) >= 2:
  chan = str(sys.argv[1]).upper()
else:
  chan = "O1"

if chan == "OA":
    dev = "/dev/i2c-6"
    p0_reglist = [
        0,  # 0x01      Power-Down and Reset
    #    1,  # 0x02      Global Interrupt Status
        2,  # 0x03      Port A Control
        3,  # 0x04      Port A Control
    #    4,  # 0x05      Port B Control
    #    5,  # 0x06      Port B Control
        6,  # 0x07      Transmitter Control
        7,  # 0x08      Transmitter Control
        8,  # 0x09      Transmitter Control
        9,  # 0x0A      SRC and DIT Status
    #    10, # 0x0B      SRC and DIT Interrupt Mask
    #    11, # 0x0C      SRC and DIT Interrupt Mask
    #    12, # 0x0D      Receiver Control
    #    13, # 0x0E      Receiver Control
    #    14, # 0x0F-0x11 Receiver PLL Configuration
    #    15, # 0x12      Non-PCM Audio Detection
    #    16, # 0x13      Receiver Status
    #    17, # 0x14      Receiver Status
    #    18, # 0x15      Receiver Status
    #    19, # 0x16      Receiver Interrupt Mask
    #    20, # 0x17      Receiver Interrupt Mask
    #    21, # 0x18      Receiver Interrupt Mode
    #    22, # 0x19      Receiver Interrupt Mode
    #    23, # 0x1A      Receiver Interrupt Mode
    #    24, # 0x1B      General-Purpose Out (GPO1)
    #    25, # 0x1C      General-Purpose Out (GPO2)
    #    26, # 0x1D      General-Purpose Out (GPO3)
    #    27, # 0x1E      General-Purpose Out (GPO4)
    #    28, # 0x1F      Audio CD Q-Channel Sub-Code
    #    29, # 0x20      Audio CD Q-Channel Sub-Code
    #    30, # 0x21      Audio CD Q-Channel Sub-Code
    #    31, # 0x22      Audio CD Q-Channel Sub-Code
    #    32, # 0x23      Audio CD Q-Channel Sub-Code
    #    33, # 0x24      Audio CD Q-Channel Sub-Code
    #    34, # 0x25      Audio CD Q-Channel Sub-Code
    #    35, # 0x26      Audio CD Q-Channel Sub-Code
    #    36, # 0x27      Audio CD Q-Channel Sub-Code
    #    37, # 0x28      Audio CD Q-Channel Sub-Code
    #    38, # 0x29-0x2A PC Burst Preamble
    #    39, # 0x2B-0x2C PD Burst Preamble
        40, # 0x2D      SRC Control
        41, # 0x2E      SRC Control
        42, # 0x2F      SRC Control
        43, # 0x30      SRC Control Right Attenuation
        44, # 0x31      SRC Control Left Attenuation
        45, # 0x32-0x33 SRC Input: Output Ratio
    ]
    p1_reglist = [
    #    0,  # 0x00      DIR Channel Status Ch1 Byte 0
    #    1,  # 0x01      DIR Channel Status Ch2 Byte 0
    #    2,  # 0x02      DIR Channel Status Ch1 Byte 1
    #    3,  # 0x03      DIR Channel Status Ch2 Byte 1
    #    4,  # 0x04      DIR Channel Status Ch1 Byte 2
    #    5,  # 0x05      DIR Channel Status Ch2 Byte 2
    #    6,  # 0x06      DIR Channel Status Ch1 Byte 3
    #    7,  # 0x07      DIR Channel Status Ch2 Byte 3
    #    8,  # 0x08      DIR Channel Status Ch1 Byte 4
    #    9,  # 0x09      DIR Channel Status Ch2 Byte 4
    #    10, # 0x0A      DIR Channel Status Ch1 Byte 5
    #    11, # 0x0B      DIR Channel Status Ch2 Byte 5
    #    12, # 0x0C      DIR Channel Status Ch1 Byte 6
    #    13, # 0x0D      DIR Channel Status Ch2 Byte 6
    #    14, # 0x0E      DIR Channel Status Ch1 Byte 7
    #    15, # 0x0F      DIR Channel Status Ch2 Byte 7
    #    16, # 0x10      DIR Channel Status Ch1 Byte 8
    #    17, # 0x11      DIR Channel Status Ch2 Byte 8
    #    18, # 0x12      DIR Channel Status Ch1 Byte 9
    #    19, # 0x13      DIR Channel Status Ch2 Byte 9
    #    20, # 0x14      DIR Channel Status Ch1 Byte 10
    #    21, # 0x15      DIR Channel Status Ch2 Byte 10
    #    22, # 0x16      DIR Channel Status Ch1 Byte 11
    #    23, # 0x17      DIR Channel Status Ch2 Byte 11
    #    24, # 0x18      DIR Channel Status Ch1 Byte 12
    #    25, # 0x19      DIR Channel Status Ch2 Byte 12
    #    26, # 0x1A      DIR Channel Status Ch1 Byte 13
    #    27, # 0x1B      DIR Channel Status Ch2 Byte 13
    #    28, # 0x1C      DIR Channel Status Ch1 Byte 14
    #    29, # 0x1D      DIR Channel Status Ch2 Byte 14
    #    30, # 0x1E      DIR Channel Status Ch1 Byte 15
    #    31, # 0x1F      DIR Channel Status Ch2 Byte 15
    #    32, # 0x20      DIR Channel Status Ch1 Byte 16
    #    33, # 0x21      DIR Channel Status Ch2 Byte 16
    #    34, # 0x22      DIR Channel Status Ch1 Byte 17
    #    35, # 0x23      DIR Channel Status Ch2 Byte 17
    #    36, # 0x24      DIR Channel Status Ch1 Byte 18
    #    37, # 0x25      DIR Channel Status Ch2 Byte 18
    #    38, # 0x26      DIR Channel Status Ch1 Byte 19
    #    39, # 0x27      DIR Channel Status Ch2 Byte 19
    #    40, # 0x28      DIR Channel Status Ch1 Byte 20
    #    41, # 0x29      DIR Channel Status Ch2 Byte 20
    #    42, # 0x2A      DIR Channel Status Ch1 Byte 21
    #    43, # 0x2B      DIR Channel Status Ch2 Byte 21
    #    44, # 0x2C      DIR Channel Status Ch1 Byte 22
    #    45, # 0x2D      DIR Channel Status Ch2 Byte 22
    #    46, # 0x2E      DIR Channel Status Ch1 Byte 23
    #    47, # 0x2F      DIR Channel Status Ch2 Byte 23
    #    48, # 0x40      DIR User Data Ch2 Byte 0
    #    49, # 0x41      DIR User Data Ch1 Byte 0
    #    50, # 0x42      DIR User Data Ch2 Byte 1
    #    51, # 0x43      DIR User Data Ch1 Byte 1
    #    52, # 0x44      DIR User Data Ch2 Byte 2
    #    53, # 0x45      DIR User Data Ch1 Byte 2
    #    54, # 0x46      DIR User Data Ch2 Byte 3
    #    55, # 0x47      DIR User Data Ch1 Byte 3
    #    56, # 0x48      DIR User Data Ch2 Byte 4
    #    57, # 0x49      DIR User Data Ch1 Byte 4
    #    58, # 0x4A      DIR User Data Ch2 Byte 5
    #    59, # 0x4B      DIR User Data Ch1 Byte 5
    #    60, # 0x4C      DIR User Data Ch2 Byte 6
    #    61, # 0x4D      DIR User Data Ch1 Byte 6
    #    62, # 0x4E      DIR User Data Ch2 Byte 7
    #    63, # 0x4F      DIR User Data Ch1 Byte 7
    #    64, # 0x50      DIR User Data Ch2 Byte 8
    #    65, # 0x51      DIR User Data Ch1 Byte 8
    #    66, # 0x52      DIR User Data Ch2 Byte 9
    #    67, # 0x53      DIR User Data Ch1 Byte 9
    #    68, # 0x54      DIR User Data Ch2 Byte 10
    #    69, # 0x55      DIR User Data Ch1 Byte 10
    #    70, # 0x56      DIR User Data Ch2 Byte 11
    #    71, # 0x57      DIR User Data Ch1 Byte 11
    #    72, # 0x58      DIR User Data Ch2 Byte 12
    #    73, # 0x59      DIR User Data Ch1 Byte 12
    #    74, # 0x5A      DIR User Data Ch2 Byte 13
    #    75, # 0x5B      DIR User Data Ch1 Byte 13
    #    76, # 0x5C      DIR User Data Ch2 Byte 14
    #    77, # 0x5D      DIR User Data Ch1 Byte 14
    #    78, # 0x5E      DIR User Data Ch2 Byte 15
    #    79, # 0x5F      DIR User Data Ch1 Byte 15
    #    80, # 0x60      DIR User Data Ch2 Byte 16
    #    81, # 0x61      DIR User Data Ch1 Byte 16
    #    82, # 0x62      DIR User Data Ch2 Byte 17
    #    83, # 0x63      DIR User Data Ch1 Byte 17
    #    84, # 0x64      DIR User Data Ch2 Byte 18
    #    85, # 0x65      DIR User Data Ch1 Byte 18
    #    86, # 0x66      DIR User Data Ch2 Byte 19
    #    87, # 0x67      DIR User Data Ch1 Byte 19
    #    88, # 0x68      DIR User Data Ch2 Byte 20
    #    89, # 0x69      DIR User Data Ch1 Byte 20
    #    90, # 0x6A      DIR User Data Ch2 Byte 21
    #    91, # 0x6B      DIR User Data Ch1 Byte 21
    #    92, # 0x6C      DIR User Data Ch2 Byte 22
    #    93, # 0x6D      DIR User Data Ch2 Byte 22
    #    94, # 0x6E      DIR User Data Ch1 Byte 23
    #    95, # 0x6F      DIR User Data Ch2 Byte 23
    ]
    p2_reglist = [
        0,  # 0x00      DIT Channel Status Ch1 Byte 0
        1,  # 0x01      DIT Channel Status Ch2 Byte 0
        2,  # 0x02      DIT Channel Status Ch1 Byte 1
        3,  # 0x03      DIT Channel Status Ch2 Byte 1
        4,  # 0x04      DIT Channel Status Ch1 Byte 2
        5,  # 0x05      DIT Channel Status Ch2 Byte 2
        6,  # 0x06      DIT Channel Status Ch1 Byte 3
        7,  # 0x07      DIT Channel Status Ch2 Byte 3
    #    8,  # 0x08      DIT Channel Status Ch1 Byte 4
    #    9,  # 0x09      DIT Channel Status Ch2 Byte 4
    #    10, # 0x0A      DIT Channel Status Ch1 Byte 5
    #    11, # 0x0B      DIT Channel Status Ch2 Byte 5
    #    12, # 0x0C      DIT Channel Status Ch1 Byte 6
    #    13, # 0x0D      DIT Channel Status Ch2 Byte 6
    #    14, # 0x0E      DIT Channel Status Ch1 Byte 7
    #    15, # 0x0F      DIT Channel Status Ch2 Byte 7
    #    16, # 0x10      DIT Channel Status Ch1 Byte 8
    #    17, # 0x11      DIT Channel Status Ch2 Byte 8
    #    18, # 0x12      DIT Channel Status Ch1 Byte 9
    #    19, # 0x13      DIT Channel Status Ch2 Byte 9
    #    20, # 0x14      DIT Channel Status Ch1 Byte 10
    #    21, # 0x15      DIT Channel Status Ch2 Byte 10
    #    22, # 0x16      DIT Channel Status Ch1 Byte 11
    #    23, # 0x17      DIT Channel Status Ch2 Byte 11
    #    24, # 0x18      DIT Channel Status Ch1 Byte 12
    #    25, # 0x19      DIT Channel Status Ch2 Byte 12
    #    26, # 0x1A      DIT Channel Status Ch1 Byte 13
    #    27, # 0x1B      DIT Channel Status Ch2 Byte 13
    #    28, # 0x1C      DIT Channel Status Ch1 Byte 14
    #    29, # 0x1D      DIT Channel Status Ch2 Byte 14
    #    30, # 0x1E      DIT Channel Status Ch1 Byte 15
    #    31, # 0x1F      DIT Channel Status Ch2 Byte 15
    #    32, # 0x20      DIT Channel Status Ch1 Byte 16
    #    33, # 0x21      DIT Channel Status Ch2 Byte 16
    #    34, # 0x22      DIT Channel Status Ch1 Byte 17
    #    35, # 0x23      DIT Channel Status Ch2 Byte 17
    #    36, # 0x24      DIT Channel Status Ch1 Byte 18
    #    37, # 0x25      DIT Channel Status Ch2 Byte 18
    #    38, # 0x26      DIT Channel Status Ch1 Byte 19
    #    39, # 0x27      DIT Channel Status Ch2 Byte 19
    #    40, # 0x28      DIT Channel Status Ch1 Byte 20
    #    41, # 0x29      DIT Channel Status Ch2 Byte 20
    #    42, # 0x2A      DIT Channel Status Ch1 Byte 21
    #    43, # 0x2B      DIT Channel Status Ch2 Byte 21
    #    44, # 0x2C      DIT Channel Status Ch1 Byte 22
    #    45, # 0x2D      DIT Channel Status Ch2 Byte 22
    #    46, # 0x2E      DIT Channel Status Ch1 Byte 23
    #    47, # 0x2F      DIT Channel Status Ch2 Byte 23
    #    48, # 0x40      DIT User Data Ch2 Byte 0
    #    49, # 0x41      DIT User Data Ch1 Byte 0
    #    50, # 0x42      DIT User Data Ch2 Byte 1
    #    51, # 0x43      DIT User Data Ch1 Byte 1
    #    52, # 0x44      DIT User Data Ch2 Byte 2
    #    53, # 0x45      DIT User Data Ch1 Byte 2
    #    54, # 0x46      DIT User Data Ch2 Byte 3
    #    55, # 0x47      DIT User Data Ch1 Byte 3
    #    56, # 0x48      DIT User Data Ch2 Byte 4
    #    57, # 0x49      DIT User Data Ch1 Byte 4
    #    58, # 0x4A      DIT User Data Ch2 Byte 5
    #    59, # 0x4B      DIT User Data Ch1 Byte 5
    #    60, # 0x4C      DIT User Data Ch2 Byte 6
    #    61, # 0x4D      DIT User Data Ch1 Byte 6
    #    62, # 0x4E      DIT User Data Ch2 Byte 7
    #    63, # 0x4F      DIT User Data Ch1 Byte 7
    #    64, # 0x50      DIT User Data Ch2 Byte 8
    #    65, # 0x51      DIT User Data Ch1 Byte 8
    #    66, # 0x52      DIT User Data Ch2 Byte 9
    #    67, # 0x53      DIT User Data Ch1 Byte 9
    #    68, # 0x54      DIT User Data Ch2 Byte 10
    #    69, # 0x55      DIT User Data Ch1 Byte 10
    #    70, # 0x56      DIT User Data Ch2 Byte 11
    #    71, # 0x57      DIT User Data Ch1 Byte 11
    #    72, # 0x58      DIT User Data Ch2 Byte 12
    #    73, # 0x59      DIT User Data Ch1 Byte 12
    #    74, # 0x5A      DIT User Data Ch2 Byte 13
    #    75, # 0x5B      DIT User Data Ch1 Byte 13
    #    76, # 0x5C      DIT User Data Ch2 Byte 14
    #    77, # 0x5D      DIT User Data Ch1 Byte 14
    #    78, # 0x5E      DIR User Data Ch2 Byte 15
    #    79, # 0x5F      DIT User Data Ch1 Byte 15
    #    80, # 0x60      DIT User Data Ch2 Byte 16
    #    81, # 0x61      DIT User Data Ch1 Byte 16
    #    82, # 0x62      DIT User Data Ch2 Byte 17
    #    83, # 0x63      DIT User Data Ch1 Byte 17
    #    84, # 0x64      DIT User Data Ch2 Byte 18
    #    85, # 0x65      DIT User Data Ch1 Byte 18
    #    86, # 0x66      DIT User Data Ch2 Byte 19
    #    87, # 0x67      DIT User Data Ch1 Byte 19
    #    88, # 0x68      DIT User Data Ch2 Byte 20
    #    89, # 0x69      DIT User Data Ch1 Byte 20
    #    90, # 0x6A      DIT User Data Ch2 Byte 21
    #    91, # 0x6B      DIT User Data Ch1 Byte 21
    #    92, # 0x6C      DIT User Data Ch2 Byte 22
    #    93, # 0x6D      DIT User Data Ch2 Byte 22
    #    94, # 0x6E      DIT User Data Ch1 Byte 23
    #    95, # 0x6F      DIT User Data Ch2 Byte 23
    ]
elif chan == "OB":
    dev = "/dev/i2c-7"
    p0_reglist = [
        0,  # 0x01      Power-Down and Reset
    #    1,  # 0x02      Global Interrupt Status
        2,  # 0x03      Port A Control
        3,  # 0x04      Port A Control
    #    4,  # 0x05      Port B Control
    #    5,  # 0x06      Port B Control
        6,  # 0x07      Transmitter Control
        7,  # 0x08      Transmitter Control
        8,  # 0x09      Transmitter Control
        9,  # 0x0A      SRC and DIT Status
    #    10, # 0x0B      SRC and DIT Interrupt Mask
    #    11, # 0x0C      SRC and DIT Interrupt Mask
    #    12, # 0x0D      Receiver Control
    #    13, # 0x0E      Receiver Control
    #    14, # 0x0F-0x11 Receiver PLL Configuration
    #    15, # 0x12      Non-PCM Audio Detection
    #    16, # 0x13      Receiver Status
    #    17, # 0x14      Receiver Status
    #    18, # 0x15      Receiver Status
    #    19, # 0x16      Receiver Interrupt Mask
    #    20, # 0x17      Receiver Interrupt Mask
    #    21, # 0x18      Receiver Interrupt Mode
    #    22, # 0x19      Receiver Interrupt Mode
    #    23, # 0x1A      Receiver Interrupt Mode
    #    24, # 0x1B      General-Purpose Out (GPO1)
    #    25, # 0x1C      General-Purpose Out (GPO2)
    #    26, # 0x1D      General-Purpose Out (GPO3)
    #    27, # 0x1E      General-Purpose Out (GPO4)
    #    28, # 0x1F      Audio CD Q-Channel Sub-Code
    #    29, # 0x20      Audio CD Q-Channel Sub-Code
    #    30, # 0x21      Audio CD Q-Channel Sub-Code
    #    31, # 0x22      Audio CD Q-Channel Sub-Code
    #    32, # 0x23      Audio CD Q-Channel Sub-Code
    #    33, # 0x24      Audio CD Q-Channel Sub-Code
    #    34, # 0x25      Audio CD Q-Channel Sub-Code
    #    35, # 0x26      Audio CD Q-Channel Sub-Code
    #    36, # 0x27      Audio CD Q-Channel Sub-Code
    #    37, # 0x28      Audio CD Q-Channel Sub-Code
    #    38, # 0x29-0x2A PC Burst Preamble
    #    39, # 0x2B-0x2C PD Burst Preamble
        40, # 0x2D      SRC Control
        41, # 0x2E      SRC Control
        42, # 0x2F      SRC Control
        43, # 0x30      SRC Control Right Attenuation
        44, # 0x31      SRC Control Left Attenuation
        45, # 0x32-0x33 SRC Input: Output Ratio
    ]
    p1_reglist = [
    #    0,  # 0x00      DIR Channel Status Ch1 Byte 0
    #    1,  # 0x01      DIR Channel Status Ch2 Byte 0
    #    2,  # 0x02      DIR Channel Status Ch1 Byte 1
    #    3,  # 0x03      DIR Channel Status Ch2 Byte 1
    #    4,  # 0x04      DIR Channel Status Ch1 Byte 2
    #    5,  # 0x05      DIR Channel Status Ch2 Byte 2
    #    6,  # 0x06      DIR Channel Status Ch1 Byte 3
    #    7,  # 0x07      DIR Channel Status Ch2 Byte 3
    #    8,  # 0x08      DIR Channel Status Ch1 Byte 4
    #    9,  # 0x09      DIR Channel Status Ch2 Byte 4
    #    10, # 0x0A      DIR Channel Status Ch1 Byte 5
    #    11, # 0x0B      DIR Channel Status Ch2 Byte 5
    #    12, # 0x0C      DIR Channel Status Ch1 Byte 6
    #    13, # 0x0D      DIR Channel Status Ch2 Byte 6
    #    14, # 0x0E      DIR Channel Status Ch1 Byte 7
    #    15, # 0x0F      DIR Channel Status Ch2 Byte 7
    #    16, # 0x10      DIR Channel Status Ch1 Byte 8
    #    17, # 0x11      DIR Channel Status Ch2 Byte 8
    #    18, # 0x12      DIR Channel Status Ch1 Byte 9
    #    19, # 0x13      DIR Channel Status Ch2 Byte 9
    #    20, # 0x14      DIR Channel Status Ch1 Byte 10
    #    21, # 0x15      DIR Channel Status Ch2 Byte 10
    #    22, # 0x16      DIR Channel Status Ch1 Byte 11
    #    23, # 0x17      DIR Channel Status Ch2 Byte 11
    #    24, # 0x18      DIR Channel Status Ch1 Byte 12
    #    25, # 0x19      DIR Channel Status Ch2 Byte 12
    #    26, # 0x1A      DIR Channel Status Ch1 Byte 13
    #    27, # 0x1B      DIR Channel Status Ch2 Byte 13
    #    28, # 0x1C      DIR Channel Status Ch1 Byte 14
    #    29, # 0x1D      DIR Channel Status Ch2 Byte 14
    #    30, # 0x1E      DIR Channel Status Ch1 Byte 15
    #    31, # 0x1F      DIR Channel Status Ch2 Byte 15
    #    32, # 0x20      DIR Channel Status Ch1 Byte 16
    #    33, # 0x21      DIR Channel Status Ch2 Byte 16
    #    34, # 0x22      DIR Channel Status Ch1 Byte 17
    #    35, # 0x23      DIR Channel Status Ch2 Byte 17
    #    36, # 0x24      DIR Channel Status Ch1 Byte 18
    #    37, # 0x25      DIR Channel Status Ch2 Byte 18
    #    38, # 0x26      DIR Channel Status Ch1 Byte 19
    #    39, # 0x27      DIR Channel Status Ch2 Byte 19
    #    40, # 0x28      DIR Channel Status Ch1 Byte 20
    #    41, # 0x29      DIR Channel Status Ch2 Byte 20
    #    42, # 0x2A      DIR Channel Status Ch1 Byte 21
    #    43, # 0x2B      DIR Channel Status Ch2 Byte 21
    #    44, # 0x2C      DIR Channel Status Ch1 Byte 22
    #    45, # 0x2D      DIR Channel Status Ch2 Byte 22
    #    46, # 0x2E      DIR Channel Status Ch1 Byte 23
    #    47, # 0x2F      DIR Channel Status Ch2 Byte 23
    #    48, # 0x40      DIR User Data Ch2 Byte 0
    #    49, # 0x41      DIR User Data Ch1 Byte 0
    #    50, # 0x42      DIR User Data Ch2 Byte 1
    #    51, # 0x43      DIR User Data Ch1 Byte 1
    #    52, # 0x44      DIR User Data Ch2 Byte 2
    #    53, # 0x45      DIR User Data Ch1 Byte 2
    #    54, # 0x46      DIR User Data Ch2 Byte 3
    #    55, # 0x47      DIR User Data Ch1 Byte 3
    #    56, # 0x48      DIR User Data Ch2 Byte 4
    #    57, # 0x49      DIR User Data Ch1 Byte 4
    #    58, # 0x4A      DIR User Data Ch2 Byte 5
    #    59, # 0x4B      DIR User Data Ch1 Byte 5
    #    60, # 0x4C      DIR User Data Ch2 Byte 6
    #    61, # 0x4D      DIR User Data Ch1 Byte 6
    #    62, # 0x4E      DIR User Data Ch2 Byte 7
    #    63, # 0x4F      DIR User Data Ch1 Byte 7
    #    64, # 0x50      DIR User Data Ch2 Byte 8
    #    65, # 0x51      DIR User Data Ch1 Byte 8
    #    66, # 0x52      DIR User Data Ch2 Byte 9
    #    67, # 0x53      DIR User Data Ch1 Byte 9
    #    68, # 0x54      DIR User Data Ch2 Byte 10
    #    69, # 0x55      DIR User Data Ch1 Byte 10
    #    70, # 0x56      DIR User Data Ch2 Byte 11
    #    71, # 0x57      DIR User Data Ch1 Byte 11
    #    72, # 0x58      DIR User Data Ch2 Byte 12
    #    73, # 0x59      DIR User Data Ch1 Byte 12
    #    74, # 0x5A      DIR User Data Ch2 Byte 13
    #    75, # 0x5B      DIR User Data Ch1 Byte 13
    #    76, # 0x5C      DIR User Data Ch2 Byte 14
    #    77, # 0x5D      DIR User Data Ch1 Byte 14
    #    78, # 0x5E      DIR User Data Ch2 Byte 15
    #    79, # 0x5F      DIR User Data Ch1 Byte 15
    #    80, # 0x60      DIR User Data Ch2 Byte 16
    #    81, # 0x61      DIR User Data Ch1 Byte 16
    #    82, # 0x62      DIR User Data Ch2 Byte 17
    #    83, # 0x63      DIR User Data Ch1 Byte 17
    #    84, # 0x64      DIR User Data Ch2 Byte 18
    #    85, # 0x65      DIR User Data Ch1 Byte 18
    #    86, # 0x66      DIR User Data Ch2 Byte 19
    #    87, # 0x67      DIR User Data Ch1 Byte 19
    #    88, # 0x68      DIR User Data Ch2 Byte 20
    #    89, # 0x69      DIR User Data Ch1 Byte 20
    #    90, # 0x6A      DIR User Data Ch2 Byte 21
    #    91, # 0x6B      DIR User Data Ch1 Byte 21
    #    92, # 0x6C      DIR User Data Ch2 Byte 22
    #    93, # 0x6D      DIR User Data Ch2 Byte 22
    #    94, # 0x6E      DIR User Data Ch1 Byte 23
    #    95, # 0x6F      DIR User Data Ch2 Byte 23
    ]
    p2_reglist = [
        0,  # 0x00      DIT Channel Status Ch1 Byte 0
        1,  # 0x01      DIT Channel Status Ch2 Byte 0
        2,  # 0x02      DIT Channel Status Ch1 Byte 1
        3,  # 0x03      DIT Channel Status Ch2 Byte 1
        4,  # 0x04      DIT Channel Status Ch1 Byte 2
        5,  # 0x05      DIT Channel Status Ch2 Byte 2
        6,  # 0x06      DIT Channel Status Ch1 Byte 3
        7,  # 0x07      DIT Channel Status Ch2 Byte 3
    #    8,  # 0x08      DIT Channel Status Ch1 Byte 4
    #    9,  # 0x09      DIT Channel Status Ch2 Byte 4
    #    10, # 0x0A      DIT Channel Status Ch1 Byte 5
    #    11, # 0x0B      DIT Channel Status Ch2 Byte 5
    #    12, # 0x0C      DIT Channel Status Ch1 Byte 6
    #    13, # 0x0D      DIT Channel Status Ch2 Byte 6
    #    14, # 0x0E      DIT Channel Status Ch1 Byte 7
    #    15, # 0x0F      DIT Channel Status Ch2 Byte 7
    #    16, # 0x10      DIT Channel Status Ch1 Byte 8
    #    17, # 0x11      DIT Channel Status Ch2 Byte 8
    #    18, # 0x12      DIT Channel Status Ch1 Byte 9
    #    19, # 0x13      DIT Channel Status Ch2 Byte 9
    #    20, # 0x14      DIT Channel Status Ch1 Byte 10
    #    21, # 0x15      DIT Channel Status Ch2 Byte 10
    #    22, # 0x16      DIT Channel Status Ch1 Byte 11
    #    23, # 0x17      DIT Channel Status Ch2 Byte 11
    #    24, # 0x18      DIT Channel Status Ch1 Byte 12
    #    25, # 0x19      DIT Channel Status Ch2 Byte 12
    #    26, # 0x1A      DIT Channel Status Ch1 Byte 13
    #    27, # 0x1B      DIT Channel Status Ch2 Byte 13
    #    28, # 0x1C      DIT Channel Status Ch1 Byte 14
    #    29, # 0x1D      DIT Channel Status Ch2 Byte 14
    #    30, # 0x1E      DIT Channel Status Ch1 Byte 15
    #    31, # 0x1F      DIT Channel Status Ch2 Byte 15
    #    32, # 0x20      DIT Channel Status Ch1 Byte 16
    #    33, # 0x21      DIT Channel Status Ch2 Byte 16
    #    34, # 0x22      DIT Channel Status Ch1 Byte 17
    #    35, # 0x23      DIT Channel Status Ch2 Byte 17
    #    36, # 0x24      DIT Channel Status Ch1 Byte 18
    #    37, # 0x25      DIT Channel Status Ch2 Byte 18
    #    38, # 0x26      DIT Channel Status Ch1 Byte 19
    #    39, # 0x27      DIT Channel Status Ch2 Byte 19
    #    40, # 0x28      DIT Channel Status Ch1 Byte 20
    #    41, # 0x29      DIT Channel Status Ch2 Byte 20
    #    42, # 0x2A      DIT Channel Status Ch1 Byte 21
    #    43, # 0x2B      DIT Channel Status Ch2 Byte 21
    #    44, # 0x2C      DIT Channel Status Ch1 Byte 22
    #    45, # 0x2D      DIT Channel Status Ch2 Byte 22
    #    46, # 0x2E      DIT Channel Status Ch1 Byte 23
    #    47, # 0x2F      DIT Channel Status Ch2 Byte 23
    #    48, # 0x40      DIT User Data Ch2 Byte 0
    #    49, # 0x41      DIT User Data Ch1 Byte 0
    #    50, # 0x42      DIT User Data Ch2 Byte 1
    #    51, # 0x43      DIT User Data Ch1 Byte 1
    #    52, # 0x44      DIT User Data Ch2 Byte 2
    #    53, # 0x45      DIT User Data Ch1 Byte 2
    #    54, # 0x46      DIT User Data Ch2 Byte 3
    #    55, # 0x47      DIT User Data Ch1 Byte 3
    #    56, # 0x48      DIT User Data Ch2 Byte 4
    #    57, # 0x49      DIT User Data Ch1 Byte 4
    #    58, # 0x4A      DIT User Data Ch2 Byte 5
    #    59, # 0x4B      DIT User Data Ch1 Byte 5
    #    60, # 0x4C      DIT User Data Ch2 Byte 6
    #    61, # 0x4D      DIT User Data Ch1 Byte 6
    #    62, # 0x4E      DIT User Data Ch2 Byte 7
    #    63, # 0x4F      DIT User Data Ch1 Byte 7
    #    64, # 0x50      DIT User Data Ch2 Byte 8
    #    65, # 0x51      DIT User Data Ch1 Byte 8
    #    66, # 0x52      DIT User Data Ch2 Byte 9
    #    67, # 0x53      DIT User Data Ch1 Byte 9
    #    68, # 0x54      DIT User Data Ch2 Byte 10
    #    69, # 0x55      DIT User Data Ch1 Byte 10
    #    70, # 0x56      DIT User Data Ch2 Byte 11
    #    71, # 0x57      DIT User Data Ch1 Byte 11
    #    72, # 0x58      DIT User Data Ch2 Byte 12
    #    73, # 0x59      DIT User Data Ch1 Byte 12
    #    74, # 0x5A      DIT User Data Ch2 Byte 13
    #    75, # 0x5B      DIT User Data Ch1 Byte 13
    #    76, # 0x5C      DIT User Data Ch2 Byte 14
    #    77, # 0x5D      DIT User Data Ch1 Byte 14
    #    78, # 0x5E      DIR User Data Ch2 Byte 15
    #    79, # 0x5F      DIT User Data Ch1 Byte 15
    #    80, # 0x60      DIT User Data Ch2 Byte 16
    #    81, # 0x61      DIT User Data Ch1 Byte 16
    #    82, # 0x62      DIT User Data Ch2 Byte 17
    #    83, # 0x63      DIT User Data Ch1 Byte 17
    #    84, # 0x64      DIT User Data Ch2 Byte 18
    #    85, # 0x65      DIT User Data Ch1 Byte 18
    #    86, # 0x66      DIT User Data Ch2 Byte 19
    #    87, # 0x67      DIT User Data Ch1 Byte 19
    #    88, # 0x68      DIT User Data Ch2 Byte 20
    #    89, # 0x69      DIT User Data Ch1 Byte 20
    #    90, # 0x6A      DIT User Data Ch2 Byte 21
    #    91, # 0x6B      DIT User Data Ch1 Byte 21
    #    92, # 0x6C      DIT User Data Ch2 Byte 22
    #    93, # 0x6D      DIT User Data Ch2 Byte 22
    #    94, # 0x6E      DIT User Data Ch1 Byte 23
    #    95, # 0x6F      DIT User Data Ch2 Byte 23
    ]
elif chan == "OC":
    dev = "/dev/i2c-8"
    p0_reglist = [
        0,  # 0x01      Power-Down and Reset
    #    1,  # 0x02      Global Interrupt Status
        2,  # 0x03      Port A Control
        3,  # 0x04      Port A Control
    #    4,  # 0x05      Port B Control
    #    5,  # 0x06      Port B Control
        6,  # 0x07      Transmitter Control
        7,  # 0x08      Transmitter Control
        8,  # 0x09      Transmitter Control
        9,  # 0x0A      SRC and DIT Status
    #    10, # 0x0B      SRC and DIT Interrupt Mask
    #    11, # 0x0C      SRC and DIT Interrupt Mask
    #    12, # 0x0D      Receiver Control
    #    13, # 0x0E      Receiver Control
    #    14, # 0x0F-0x11 Receiver PLL Configuration
    #    15, # 0x12      Non-PCM Audio Detection
    #    16, # 0x13      Receiver Status
    #    17, # 0x14      Receiver Status
    #    18, # 0x15      Receiver Status
    #    19, # 0x16      Receiver Interrupt Mask
    #    20, # 0x17      Receiver Interrupt Mask
    #    21, # 0x18      Receiver Interrupt Mode
    #    22, # 0x19      Receiver Interrupt Mode
    #    23, # 0x1A      Receiver Interrupt Mode
    #    24, # 0x1B      General-Purpose Out (GPO1)
    #    25, # 0x1C      General-Purpose Out (GPO2)
    #    26, # 0x1D      General-Purpose Out (GPO3)
    #    27, # 0x1E      General-Purpose Out (GPO4)
    #    28, # 0x1F      Audio CD Q-Channel Sub-Code
    #    29, # 0x20      Audio CD Q-Channel Sub-Code
    #    30, # 0x21      Audio CD Q-Channel Sub-Code
    #    31, # 0x22      Audio CD Q-Channel Sub-Code
    #    32, # 0x23      Audio CD Q-Channel Sub-Code
    #    33, # 0x24      Audio CD Q-Channel Sub-Code
    #    34, # 0x25      Audio CD Q-Channel Sub-Code
    #    35, # 0x26      Audio CD Q-Channel Sub-Code
    #    36, # 0x27      Audio CD Q-Channel Sub-Code
    #    37, # 0x28      Audio CD Q-Channel Sub-Code
    #    38, # 0x29-0x2A PC Burst Preamble
    #    39, # 0x2B-0x2C PD Burst Preamble
        40, # 0x2D      SRC Control
        41, # 0x2E      SRC Control
        42, # 0x2F      SRC Control
        43, # 0x30      SRC Control Right Attenuation
        44, # 0x31      SRC Control Left Attenuation
        45, # 0x32-0x33 SRC Input: Output Ratio
    ]
    p1_reglist = [
    #    0,  # 0x00      DIR Channel Status Ch1 Byte 0
    #    1,  # 0x01      DIR Channel Status Ch2 Byte 0
    #    2,  # 0x02      DIR Channel Status Ch1 Byte 1
    #    3,  # 0x03      DIR Channel Status Ch2 Byte 1
    #    4,  # 0x04      DIR Channel Status Ch1 Byte 2
    #    5,  # 0x05      DIR Channel Status Ch2 Byte 2
    #    6,  # 0x06      DIR Channel Status Ch1 Byte 3
    #    7,  # 0x07      DIR Channel Status Ch2 Byte 3
    #    8,  # 0x08      DIR Channel Status Ch1 Byte 4
    #    9,  # 0x09      DIR Channel Status Ch2 Byte 4
    #    10, # 0x0A      DIR Channel Status Ch1 Byte 5
    #    11, # 0x0B      DIR Channel Status Ch2 Byte 5
    #    12, # 0x0C      DIR Channel Status Ch1 Byte 6
    #    13, # 0x0D      DIR Channel Status Ch2 Byte 6
    #    14, # 0x0E      DIR Channel Status Ch1 Byte 7
    #    15, # 0x0F      DIR Channel Status Ch2 Byte 7
    #    16, # 0x10      DIR Channel Status Ch1 Byte 8
    #    17, # 0x11      DIR Channel Status Ch2 Byte 8
    #    18, # 0x12      DIR Channel Status Ch1 Byte 9
    #    19, # 0x13      DIR Channel Status Ch2 Byte 9
    #    20, # 0x14      DIR Channel Status Ch1 Byte 10
    #    21, # 0x15      DIR Channel Status Ch2 Byte 10
    #    22, # 0x16      DIR Channel Status Ch1 Byte 11
    #    23, # 0x17      DIR Channel Status Ch2 Byte 11
    #    24, # 0x18      DIR Channel Status Ch1 Byte 12
    #    25, # 0x19      DIR Channel Status Ch2 Byte 12
    #    26, # 0x1A      DIR Channel Status Ch1 Byte 13
    #    27, # 0x1B      DIR Channel Status Ch2 Byte 13
    #    28, # 0x1C      DIR Channel Status Ch1 Byte 14
    #    29, # 0x1D      DIR Channel Status Ch2 Byte 14
    #    30, # 0x1E      DIR Channel Status Ch1 Byte 15
    #    31, # 0x1F      DIR Channel Status Ch2 Byte 15
    #    32, # 0x20      DIR Channel Status Ch1 Byte 16
    #    33, # 0x21      DIR Channel Status Ch2 Byte 16
    #    34, # 0x22      DIR Channel Status Ch1 Byte 17
    #    35, # 0x23      DIR Channel Status Ch2 Byte 17
    #    36, # 0x24      DIR Channel Status Ch1 Byte 18
    #    37, # 0x25      DIR Channel Status Ch2 Byte 18
    #    38, # 0x26      DIR Channel Status Ch1 Byte 19
    #    39, # 0x27      DIR Channel Status Ch2 Byte 19
    #    40, # 0x28      DIR Channel Status Ch1 Byte 20
    #    41, # 0x29      DIR Channel Status Ch2 Byte 20
    #    42, # 0x2A      DIR Channel Status Ch1 Byte 21
    #    43, # 0x2B      DIR Channel Status Ch2 Byte 21
    #    44, # 0x2C      DIR Channel Status Ch1 Byte 22
    #    45, # 0x2D      DIR Channel Status Ch2 Byte 22
    #    46, # 0x2E      DIR Channel Status Ch1 Byte 23
    #    47, # 0x2F      DIR Channel Status Ch2 Byte 23
    #    48, # 0x40      DIR User Data Ch2 Byte 0
    #    49, # 0x41      DIR User Data Ch1 Byte 0
    #    50, # 0x42      DIR User Data Ch2 Byte 1
    #    51, # 0x43      DIR User Data Ch1 Byte 1
    #    52, # 0x44      DIR User Data Ch2 Byte 2
    #    53, # 0x45      DIR User Data Ch1 Byte 2
    #    54, # 0x46      DIR User Data Ch2 Byte 3
    #    55, # 0x47      DIR User Data Ch1 Byte 3
    #    56, # 0x48      DIR User Data Ch2 Byte 4
    #    57, # 0x49      DIR User Data Ch1 Byte 4
    #    58, # 0x4A      DIR User Data Ch2 Byte 5
    #    59, # 0x4B      DIR User Data Ch1 Byte 5
    #    60, # 0x4C      DIR User Data Ch2 Byte 6
    #    61, # 0x4D      DIR User Data Ch1 Byte 6
    #    62, # 0x4E      DIR User Data Ch2 Byte 7
    #    63, # 0x4F      DIR User Data Ch1 Byte 7
    #    64, # 0x50      DIR User Data Ch2 Byte 8
    #    65, # 0x51      DIR User Data Ch1 Byte 8
    #    66, # 0x52      DIR User Data Ch2 Byte 9
    #    67, # 0x53      DIR User Data Ch1 Byte 9
    #    68, # 0x54      DIR User Data Ch2 Byte 10
    #    69, # 0x55      DIR User Data Ch1 Byte 10
    #    70, # 0x56      DIR User Data Ch2 Byte 11
    #    71, # 0x57      DIR User Data Ch1 Byte 11
    #    72, # 0x58      DIR User Data Ch2 Byte 12
    #    73, # 0x59      DIR User Data Ch1 Byte 12
    #    74, # 0x5A      DIR User Data Ch2 Byte 13
    #    75, # 0x5B      DIR User Data Ch1 Byte 13
    #    76, # 0x5C      DIR User Data Ch2 Byte 14
    #    77, # 0x5D      DIR User Data Ch1 Byte 14
    #    78, # 0x5E      DIR User Data Ch2 Byte 15
    #    79, # 0x5F      DIR User Data Ch1 Byte 15
    #    80, # 0x60      DIR User Data Ch2 Byte 16
    #    81, # 0x61      DIR User Data Ch1 Byte 16
    #    82, # 0x62      DIR User Data Ch2 Byte 17
    #    83, # 0x63      DIR User Data Ch1 Byte 17
    #    84, # 0x64      DIR User Data Ch2 Byte 18
    #    85, # 0x65      DIR User Data Ch1 Byte 18
    #    86, # 0x66      DIR User Data Ch2 Byte 19
    #    87, # 0x67      DIR User Data Ch1 Byte 19
    #    88, # 0x68      DIR User Data Ch2 Byte 20
    #    89, # 0x69      DIR User Data Ch1 Byte 20
    #    90, # 0x6A      DIR User Data Ch2 Byte 21
    #    91, # 0x6B      DIR User Data Ch1 Byte 21
    #    92, # 0x6C      DIR User Data Ch2 Byte 22
    #    93, # 0x6D      DIR User Data Ch2 Byte 22
    #    94, # 0x6E      DIR User Data Ch1 Byte 23
    #    95, # 0x6F      DIR User Data Ch2 Byte 23
    ]
    p2_reglist = [
        0,  # 0x00      DIT Channel Status Ch1 Byte 0
        1,  # 0x01      DIT Channel Status Ch2 Byte 0
        2,  # 0x02      DIT Channel Status Ch1 Byte 1
        3,  # 0x03      DIT Channel Status Ch2 Byte 1
        4,  # 0x04      DIT Channel Status Ch1 Byte 2
        5,  # 0x05      DIT Channel Status Ch2 Byte 2
        6,  # 0x06      DIT Channel Status Ch1 Byte 3
        7,  # 0x07      DIT Channel Status Ch2 Byte 3
    #    8,  # 0x08      DIT Channel Status Ch1 Byte 4
    #    9,  # 0x09      DIT Channel Status Ch2 Byte 4
    #    10, # 0x0A      DIT Channel Status Ch1 Byte 5
    #    11, # 0x0B      DIT Channel Status Ch2 Byte 5
    #    12, # 0x0C      DIT Channel Status Ch1 Byte 6
    #    13, # 0x0D      DIT Channel Status Ch2 Byte 6
    #    14, # 0x0E      DIT Channel Status Ch1 Byte 7
    #    15, # 0x0F      DIT Channel Status Ch2 Byte 7
    #    16, # 0x10      DIT Channel Status Ch1 Byte 8
    #    17, # 0x11      DIT Channel Status Ch2 Byte 8
    #    18, # 0x12      DIT Channel Status Ch1 Byte 9
    #    19, # 0x13      DIT Channel Status Ch2 Byte 9
    #    20, # 0x14      DIT Channel Status Ch1 Byte 10
    #    21, # 0x15      DIT Channel Status Ch2 Byte 10
    #    22, # 0x16      DIT Channel Status Ch1 Byte 11
    #    23, # 0x17      DIT Channel Status Ch2 Byte 11
    #    24, # 0x18      DIT Channel Status Ch1 Byte 12
    #    25, # 0x19      DIT Channel Status Ch2 Byte 12
    #    26, # 0x1A      DIT Channel Status Ch1 Byte 13
    #    27, # 0x1B      DIT Channel Status Ch2 Byte 13
    #    28, # 0x1C      DIT Channel Status Ch1 Byte 14
    #    29, # 0x1D      DIT Channel Status Ch2 Byte 14
    #    30, # 0x1E      DIT Channel Status Ch1 Byte 15
    #    31, # 0x1F      DIT Channel Status Ch2 Byte 15
    #    32, # 0x20      DIT Channel Status Ch1 Byte 16
    #    33, # 0x21      DIT Channel Status Ch2 Byte 16
    #    34, # 0x22      DIT Channel Status Ch1 Byte 17
    #    35, # 0x23      DIT Channel Status Ch2 Byte 17
    #    36, # 0x24      DIT Channel Status Ch1 Byte 18
    #    37, # 0x25      DIT Channel Status Ch2 Byte 18
    #    38, # 0x26      DIT Channel Status Ch1 Byte 19
    #    39, # 0x27      DIT Channel Status Ch2 Byte 19
    #    40, # 0x28      DIT Channel Status Ch1 Byte 20
    #    41, # 0x29      DIT Channel Status Ch2 Byte 20
    #    42, # 0x2A      DIT Channel Status Ch1 Byte 21
    #    43, # 0x2B      DIT Channel Status Ch2 Byte 21
    #    44, # 0x2C      DIT Channel Status Ch1 Byte 22
    #    45, # 0x2D      DIT Channel Status Ch2 Byte 22
    #    46, # 0x2E      DIT Channel Status Ch1 Byte 23
    #    47, # 0x2F      DIT Channel Status Ch2 Byte 23
    #    48, # 0x40      DIT User Data Ch2 Byte 0
    #    49, # 0x41      DIT User Data Ch1 Byte 0
    #    50, # 0x42      DIT User Data Ch2 Byte 1
    #    51, # 0x43      DIT User Data Ch1 Byte 1
    #    52, # 0x44      DIT User Data Ch2 Byte 2
    #    53, # 0x45      DIT User Data Ch1 Byte 2
    #    54, # 0x46      DIT User Data Ch2 Byte 3
    #    55, # 0x47      DIT User Data Ch1 Byte 3
    #    56, # 0x48      DIT User Data Ch2 Byte 4
    #    57, # 0x49      DIT User Data Ch1 Byte 4
    #    58, # 0x4A      DIT User Data Ch2 Byte 5
    #    59, # 0x4B      DIT User Data Ch1 Byte 5
    #    60, # 0x4C      DIT User Data Ch2 Byte 6
    #    61, # 0x4D      DIT User Data Ch1 Byte 6
    #    62, # 0x4E      DIT User Data Ch2 Byte 7
    #    63, # 0x4F      DIT User Data Ch1 Byte 7
    #    64, # 0x50      DIT User Data Ch2 Byte 8
    #    65, # 0x51      DIT User Data Ch1 Byte 8
    #    66, # 0x52      DIT User Data Ch2 Byte 9
    #    67, # 0x53      DIT User Data Ch1 Byte 9
    #    68, # 0x54      DIT User Data Ch2 Byte 10
    #    69, # 0x55      DIT User Data Ch1 Byte 10
    #    70, # 0x56      DIT User Data Ch2 Byte 11
    #    71, # 0x57      DIT User Data Ch1 Byte 11
    #    72, # 0x58      DIT User Data Ch2 Byte 12
    #    73, # 0x59      DIT User Data Ch1 Byte 12
    #    74, # 0x5A      DIT User Data Ch2 Byte 13
    #    75, # 0x5B      DIT User Data Ch1 Byte 13
    #    76, # 0x5C      DIT User Data Ch2 Byte 14
    #    77, # 0x5D      DIT User Data Ch1 Byte 14
    #    78, # 0x5E      DIR User Data Ch2 Byte 15
    #    79, # 0x5F      DIT User Data Ch1 Byte 15
    #    80, # 0x60      DIT User Data Ch2 Byte 16
    #    81, # 0x61      DIT User Data Ch1 Byte 16
    #    82, # 0x62      DIT User Data Ch2 Byte 17
    #    83, # 0x63      DIT User Data Ch1 Byte 17
    #    84, # 0x64      DIT User Data Ch2 Byte 18
    #    85, # 0x65      DIT User Data Ch1 Byte 18
    #    86, # 0x66      DIT User Data Ch2 Byte 19
    #    87, # 0x67      DIT User Data Ch1 Byte 19
    #    88, # 0x68      DIT User Data Ch2 Byte 20
    #    89, # 0x69      DIT User Data Ch1 Byte 20
    #    90, # 0x6A      DIT User Data Ch2 Byte 21
    #    91, # 0x6B      DIT User Data Ch1 Byte 21
    #    92, # 0x6C      DIT User Data Ch2 Byte 22
    #    93, # 0x6D      DIT User Data Ch2 Byte 22
    #    94, # 0x6E      DIT User Data Ch1 Byte 23
    #    95, # 0x6F      DIT User Data Ch2 Byte 23
    ]
elif chan == "OD":
    dev = "/dev/i2c-9"
    p0_reglist = [
        0,  # 0x01      Power-Down and Reset
    #    1,  # 0x02      Global Interrupt Status
        2,  # 0x03      Port A Control
        3,  # 0x04      Port A Control
    #    4,  # 0x05      Port B Control
    #    5,  # 0x06      Port B Control
        6,  # 0x07      Transmitter Control
        7,  # 0x08      Transmitter Control
        8,  # 0x09      Transmitter Control
        9,  # 0x0A      SRC and DIT Status
    #    10, # 0x0B      SRC and DIT Interrupt Mask
    #    11, # 0x0C      SRC and DIT Interrupt Mask
    #    12, # 0x0D      Receiver Control
    #    13, # 0x0E      Receiver Control
    #    14, # 0x0F-0x11 Receiver PLL Configuration
    #    15, # 0x12      Non-PCM Audio Detection
    #    16, # 0x13      Receiver Status
    #    17, # 0x14      Receiver Status
    #    18, # 0x15      Receiver Status
    #    19, # 0x16      Receiver Interrupt Mask
    #    20, # 0x17      Receiver Interrupt Mask
    #    21, # 0x18      Receiver Interrupt Mode
    #    22, # 0x19      Receiver Interrupt Mode
    #    23, # 0x1A      Receiver Interrupt Mode
    #    24, # 0x1B      General-Purpose Out (GPO1)
    #    25, # 0x1C      General-Purpose Out (GPO2)
    #    26, # 0x1D      General-Purpose Out (GPO3)
    #    27, # 0x1E      General-Purpose Out (GPO4)
    #    28, # 0x1F      Audio CD Q-Channel Sub-Code
    #    29, # 0x20      Audio CD Q-Channel Sub-Code
    #    30, # 0x21      Audio CD Q-Channel Sub-Code
    #    31, # 0x22      Audio CD Q-Channel Sub-Code
    #    32, # 0x23      Audio CD Q-Channel Sub-Code
    #    33, # 0x24      Audio CD Q-Channel Sub-Code
    #    34, # 0x25      Audio CD Q-Channel Sub-Code
    #    35, # 0x26      Audio CD Q-Channel Sub-Code
    #    36, # 0x27      Audio CD Q-Channel Sub-Code
    #    37, # 0x28      Audio CD Q-Channel Sub-Code
    #    38, # 0x29-0x2A PC Burst Preamble
    #    39, # 0x2B-0x2C PD Burst Preamble
        40, # 0x2D      SRC Control
        41, # 0x2E      SRC Control
        42, # 0x2F      SRC Control
        43, # 0x30      SRC Control Right Attenuation
        44, # 0x31      SRC Control Left Attenuation
        45, # 0x32-0x33 SRC Input: Output Ratio
    ]
    p1_reglist = [
    #    0,  # 0x00      DIR Channel Status Ch1 Byte 0
    #    1,  # 0x01      DIR Channel Status Ch2 Byte 0
    #    2,  # 0x02      DIR Channel Status Ch1 Byte 1
    #    3,  # 0x03      DIR Channel Status Ch2 Byte 1
    #    4,  # 0x04      DIR Channel Status Ch1 Byte 2
    #    5,  # 0x05      DIR Channel Status Ch2 Byte 2
    #    6,  # 0x06      DIR Channel Status Ch1 Byte 3
    #    7,  # 0x07      DIR Channel Status Ch2 Byte 3
    #    8,  # 0x08      DIR Channel Status Ch1 Byte 4
    #    9,  # 0x09      DIR Channel Status Ch2 Byte 4
    #    10, # 0x0A      DIR Channel Status Ch1 Byte 5
    #    11, # 0x0B      DIR Channel Status Ch2 Byte 5
    #    12, # 0x0C      DIR Channel Status Ch1 Byte 6
    #    13, # 0x0D      DIR Channel Status Ch2 Byte 6
    #    14, # 0x0E      DIR Channel Status Ch1 Byte 7
    #    15, # 0x0F      DIR Channel Status Ch2 Byte 7
    #    16, # 0x10      DIR Channel Status Ch1 Byte 8
    #    17, # 0x11      DIR Channel Status Ch2 Byte 8
    #    18, # 0x12      DIR Channel Status Ch1 Byte 9
    #    19, # 0x13      DIR Channel Status Ch2 Byte 9
    #    20, # 0x14      DIR Channel Status Ch1 Byte 10
    #    21, # 0x15      DIR Channel Status Ch2 Byte 10
    #    22, # 0x16      DIR Channel Status Ch1 Byte 11
    #    23, # 0x17      DIR Channel Status Ch2 Byte 11
    #    24, # 0x18      DIR Channel Status Ch1 Byte 12
    #    25, # 0x19      DIR Channel Status Ch2 Byte 12
    #    26, # 0x1A      DIR Channel Status Ch1 Byte 13
    #    27, # 0x1B      DIR Channel Status Ch2 Byte 13
    #    28, # 0x1C      DIR Channel Status Ch1 Byte 14
    #    29, # 0x1D      DIR Channel Status Ch2 Byte 14
    #    30, # 0x1E      DIR Channel Status Ch1 Byte 15
    #    31, # 0x1F      DIR Channel Status Ch2 Byte 15
    #    32, # 0x20      DIR Channel Status Ch1 Byte 16
    #    33, # 0x21      DIR Channel Status Ch2 Byte 16
    #    34, # 0x22      DIR Channel Status Ch1 Byte 17
    #    35, # 0x23      DIR Channel Status Ch2 Byte 17
    #    36, # 0x24      DIR Channel Status Ch1 Byte 18
    #    37, # 0x25      DIR Channel Status Ch2 Byte 18
    #    38, # 0x26      DIR Channel Status Ch1 Byte 19
    #    39, # 0x27      DIR Channel Status Ch2 Byte 19
    #    40, # 0x28      DIR Channel Status Ch1 Byte 20
    #    41, # 0x29      DIR Channel Status Ch2 Byte 20
    #    42, # 0x2A      DIR Channel Status Ch1 Byte 21
    #    43, # 0x2B      DIR Channel Status Ch2 Byte 21
    #    44, # 0x2C      DIR Channel Status Ch1 Byte 22
    #    45, # 0x2D      DIR Channel Status Ch2 Byte 22
    #    46, # 0x2E      DIR Channel Status Ch1 Byte 23
    #    47, # 0x2F      DIR Channel Status Ch2 Byte 23
    #    48, # 0x40      DIR User Data Ch2 Byte 0
    #    49, # 0x41      DIR User Data Ch1 Byte 0
    #    50, # 0x42      DIR User Data Ch2 Byte 1
    #    51, # 0x43      DIR User Data Ch1 Byte 1
    #    52, # 0x44      DIR User Data Ch2 Byte 2
    #    53, # 0x45      DIR User Data Ch1 Byte 2
    #    54, # 0x46      DIR User Data Ch2 Byte 3
    #    55, # 0x47      DIR User Data Ch1 Byte 3
    #    56, # 0x48      DIR User Data Ch2 Byte 4
    #    57, # 0x49      DIR User Data Ch1 Byte 4
    #    58, # 0x4A      DIR User Data Ch2 Byte 5
    #    59, # 0x4B      DIR User Data Ch1 Byte 5
    #    60, # 0x4C      DIR User Data Ch2 Byte 6
    #    61, # 0x4D      DIR User Data Ch1 Byte 6
    #    62, # 0x4E      DIR User Data Ch2 Byte 7
    #    63, # 0x4F      DIR User Data Ch1 Byte 7
    #    64, # 0x50      DIR User Data Ch2 Byte 8
    #    65, # 0x51      DIR User Data Ch1 Byte 8
    #    66, # 0x52      DIR User Data Ch2 Byte 9
    #    67, # 0x53      DIR User Data Ch1 Byte 9
    #    68, # 0x54      DIR User Data Ch2 Byte 10
    #    69, # 0x55      DIR User Data Ch1 Byte 10
    #    70, # 0x56      DIR User Data Ch2 Byte 11
    #    71, # 0x57      DIR User Data Ch1 Byte 11
    #    72, # 0x58      DIR User Data Ch2 Byte 12
    #    73, # 0x59      DIR User Data Ch1 Byte 12
    #    74, # 0x5A      DIR User Data Ch2 Byte 13
    #    75, # 0x5B      DIR User Data Ch1 Byte 13
    #    76, # 0x5C      DIR User Data Ch2 Byte 14
    #    77, # 0x5D      DIR User Data Ch1 Byte 14
    #    78, # 0x5E      DIR User Data Ch2 Byte 15
    #    79, # 0x5F      DIR User Data Ch1 Byte 15
    #    80, # 0x60      DIR User Data Ch2 Byte 16
    #    81, # 0x61      DIR User Data Ch1 Byte 16
    #    82, # 0x62      DIR User Data Ch2 Byte 17
    #    83, # 0x63      DIR User Data Ch1 Byte 17
    #    84, # 0x64      DIR User Data Ch2 Byte 18
    #    85, # 0x65      DIR User Data Ch1 Byte 18
    #    86, # 0x66      DIR User Data Ch2 Byte 19
    #    87, # 0x67      DIR User Data Ch1 Byte 19
    #    88, # 0x68      DIR User Data Ch2 Byte 20
    #    89, # 0x69      DIR User Data Ch1 Byte 20
    #    90, # 0x6A      DIR User Data Ch2 Byte 21
    #    91, # 0x6B      DIR User Data Ch1 Byte 21
    #    92, # 0x6C      DIR User Data Ch2 Byte 22
    #    93, # 0x6D      DIR User Data Ch2 Byte 22
    #    94, # 0x6E      DIR User Data Ch1 Byte 23
    #    95, # 0x6F      DIR User Data Ch2 Byte 23
    ]
    p2_reglist = [
        0,  # 0x00      DIT Channel Status Ch1 Byte 0
        1,  # 0x01      DIT Channel Status Ch2 Byte 0
        2,  # 0x02      DIT Channel Status Ch1 Byte 1
        3,  # 0x03      DIT Channel Status Ch2 Byte 1
        4,  # 0x04      DIT Channel Status Ch1 Byte 2
        5,  # 0x05      DIT Channel Status Ch2 Byte 2
        6,  # 0x06      DIT Channel Status Ch1 Byte 3
        7,  # 0x07      DIT Channel Status Ch2 Byte 3
    #    8,  # 0x08      DIT Channel Status Ch1 Byte 4
    #    9,  # 0x09      DIT Channel Status Ch2 Byte 4
    #    10, # 0x0A      DIT Channel Status Ch1 Byte 5
    #    11, # 0x0B      DIT Channel Status Ch2 Byte 5
    #    12, # 0x0C      DIT Channel Status Ch1 Byte 6
    #    13, # 0x0D      DIT Channel Status Ch2 Byte 6
    #    14, # 0x0E      DIT Channel Status Ch1 Byte 7
    #    15, # 0x0F      DIT Channel Status Ch2 Byte 7
    #    16, # 0x10      DIT Channel Status Ch1 Byte 8
    #    17, # 0x11      DIT Channel Status Ch2 Byte 8
    #    18, # 0x12      DIT Channel Status Ch1 Byte 9
    #    19, # 0x13      DIT Channel Status Ch2 Byte 9
    #    20, # 0x14      DIT Channel Status Ch1 Byte 10
    #    21, # 0x15      DIT Channel Status Ch2 Byte 10
    #    22, # 0x16      DIT Channel Status Ch1 Byte 11
    #    23, # 0x17      DIT Channel Status Ch2 Byte 11
    #    24, # 0x18      DIT Channel Status Ch1 Byte 12
    #    25, # 0x19      DIT Channel Status Ch2 Byte 12
    #    26, # 0x1A      DIT Channel Status Ch1 Byte 13
    #    27, # 0x1B      DIT Channel Status Ch2 Byte 13
    #    28, # 0x1C      DIT Channel Status Ch1 Byte 14
    #    29, # 0x1D      DIT Channel Status Ch2 Byte 14
    #    30, # 0x1E      DIT Channel Status Ch1 Byte 15
    #    31, # 0x1F      DIT Channel Status Ch2 Byte 15
    #    32, # 0x20      DIT Channel Status Ch1 Byte 16
    #    33, # 0x21      DIT Channel Status Ch2 Byte 16
    #    34, # 0x22      DIT Channel Status Ch1 Byte 17
    #    35, # 0x23      DIT Channel Status Ch2 Byte 17
    #    36, # 0x24      DIT Channel Status Ch1 Byte 18
    #    37, # 0x25      DIT Channel Status Ch2 Byte 18
    #    38, # 0x26      DIT Channel Status Ch1 Byte 19
    #    39, # 0x27      DIT Channel Status Ch2 Byte 19
    #    40, # 0x28      DIT Channel Status Ch1 Byte 20
    #    41, # 0x29      DIT Channel Status Ch2 Byte 20
    #    42, # 0x2A      DIT Channel Status Ch1 Byte 21
    #    43, # 0x2B      DIT Channel Status Ch2 Byte 21
    #    44, # 0x2C      DIT Channel Status Ch1 Byte 22
    #    45, # 0x2D      DIT Channel Status Ch2 Byte 22
    #    46, # 0x2E      DIT Channel Status Ch1 Byte 23
    #    47, # 0x2F      DIT Channel Status Ch2 Byte 23
    #    48, # 0x40      DIT User Data Ch2 Byte 0
    #    49, # 0x41      DIT User Data Ch1 Byte 0
    #    50, # 0x42      DIT User Data Ch2 Byte 1
    #    51, # 0x43      DIT User Data Ch1 Byte 1
    #    52, # 0x44      DIT User Data Ch2 Byte 2
    #    53, # 0x45      DIT User Data Ch1 Byte 2
    #    54, # 0x46      DIT User Data Ch2 Byte 3
    #    55, # 0x47      DIT User Data Ch1 Byte 3
    #    56, # 0x48      DIT User Data Ch2 Byte 4
    #    57, # 0x49      DIT User Data Ch1 Byte 4
    #    58, # 0x4A      DIT User Data Ch2 Byte 5
    #    59, # 0x4B      DIT User Data Ch1 Byte 5
    #    60, # 0x4C      DIT User Data Ch2 Byte 6
    #    61, # 0x4D      DIT User Data Ch1 Byte 6
    #    62, # 0x4E      DIT User Data Ch2 Byte 7
    #    63, # 0x4F      DIT User Data Ch1 Byte 7
    #    64, # 0x50      DIT User Data Ch2 Byte 8
    #    65, # 0x51      DIT User Data Ch1 Byte 8
    #    66, # 0x52      DIT User Data Ch2 Byte 9
    #    67, # 0x53      DIT User Data Ch1 Byte 9
    #    68, # 0x54      DIT User Data Ch2 Byte 10
    #    69, # 0x55      DIT User Data Ch1 Byte 10
    #    70, # 0x56      DIT User Data Ch2 Byte 11
    #    71, # 0x57      DIT User Data Ch1 Byte 11
    #    72, # 0x58      DIT User Data Ch2 Byte 12
    #    73, # 0x59      DIT User Data Ch1 Byte 12
    #    74, # 0x5A      DIT User Data Ch2 Byte 13
    #    75, # 0x5B      DIT User Data Ch1 Byte 13
    #    76, # 0x5C      DIT User Data Ch2 Byte 14
    #    77, # 0x5D      DIT User Data Ch1 Byte 14
    #    78, # 0x5E      DIR User Data Ch2 Byte 15
    #    79, # 0x5F      DIT User Data Ch1 Byte 15
    #    80, # 0x60      DIT User Data Ch2 Byte 16
    #    81, # 0x61      DIT User Data Ch1 Byte 16
    #    82, # 0x62      DIT User Data Ch2 Byte 17
    #    83, # 0x63      DIT User Data Ch1 Byte 17
    #    84, # 0x64      DIT User Data Ch2 Byte 18
    #    85, # 0x65      DIT User Data Ch1 Byte 18
    #    86, # 0x66      DIT User Data Ch2 Byte 19
    #    87, # 0x67      DIT User Data Ch1 Byte 19
    #    88, # 0x68      DIT User Data Ch2 Byte 20
    #    89, # 0x69      DIT User Data Ch1 Byte 20
    #    90, # 0x6A      DIT User Data Ch2 Byte 21
    #    91, # 0x6B      DIT User Data Ch1 Byte 21
    #    92, # 0x6C      DIT User Data Ch2 Byte 22
    #    93, # 0x6D      DIT User Data Ch2 Byte 22
    #    94, # 0x6E      DIT User Data Ch1 Byte 23
    #    95, # 0x6F      DIT User Data Ch2 Byte 23
    ]
elif chan == "OE":
    dev = "/dev/i2c-10"
    p0_reglist = [
        0,  # 0x01      Power-Down and Reset
    #    1,  # 0x02      Global Interrupt Status
        2,  # 0x03      Port A Control
        3,  # 0x04      Port A Control
    #    4,  # 0x05      Port B Control
    #    5,  # 0x06      Port B Control
        6,  # 0x07      Transmitter Control
        7,  # 0x08      Transmitter Control
        8,  # 0x09      Transmitter Control
        9,  # 0x0A      SRC and DIT Status
    #    10, # 0x0B      SRC and DIT Interrupt Mask
    #    11, # 0x0C      SRC and DIT Interrupt Mask
    #    12, # 0x0D      Receiver Control
    #    13, # 0x0E      Receiver Control
    #    14, # 0x0F-0x11 Receiver PLL Configuration
    #    15, # 0x12      Non-PCM Audio Detection
    #    16, # 0x13      Receiver Status
    #    17, # 0x14      Receiver Status
    #    18, # 0x15      Receiver Status
    #    19, # 0x16      Receiver Interrupt Mask
    #    20, # 0x17      Receiver Interrupt Mask
    #    21, # 0x18      Receiver Interrupt Mode
    #    22, # 0x19      Receiver Interrupt Mode
    #    23, # 0x1A      Receiver Interrupt Mode
    #    24, # 0x1B      General-Purpose Out (GPO1)
    #    25, # 0x1C      General-Purpose Out (GPO2)
    #    26, # 0x1D      General-Purpose Out (GPO3)
    #    27, # 0x1E      General-Purpose Out (GPO4)
    #    28, # 0x1F      Audio CD Q-Channel Sub-Code
    #    29, # 0x20      Audio CD Q-Channel Sub-Code
    #    30, # 0x21      Audio CD Q-Channel Sub-Code
    #    31, # 0x22      Audio CD Q-Channel Sub-Code
    #    32, # 0x23      Audio CD Q-Channel Sub-Code
    #    33, # 0x24      Audio CD Q-Channel Sub-Code
    #    34, # 0x25      Audio CD Q-Channel Sub-Code
    #    35, # 0x26      Audio CD Q-Channel Sub-Code
    #    36, # 0x27      Audio CD Q-Channel Sub-Code
    #    37, # 0x28      Audio CD Q-Channel Sub-Code
    #    38, # 0x29-0x2A PC Burst Preamble
    #    39, # 0x2B-0x2C PD Burst Preamble
        40, # 0x2D      SRC Control
        41, # 0x2E      SRC Control
        42, # 0x2F      SRC Control
        43, # 0x30      SRC Control Right Attenuation
        44, # 0x31      SRC Control Left Attenuation
        45, # 0x32-0x33 SRC Input: Output Ratio
    ]
    p1_reglist = [
    #    0,  # 0x00      DIR Channel Status Ch1 Byte 0
    #    1,  # 0x01      DIR Channel Status Ch2 Byte 0
    #    2,  # 0x02      DIR Channel Status Ch1 Byte 1
    #    3,  # 0x03      DIR Channel Status Ch2 Byte 1
    #    4,  # 0x04      DIR Channel Status Ch1 Byte 2
    #    5,  # 0x05      DIR Channel Status Ch2 Byte 2
    #    6,  # 0x06      DIR Channel Status Ch1 Byte 3
    #    7,  # 0x07      DIR Channel Status Ch2 Byte 3
    #    8,  # 0x08      DIR Channel Status Ch1 Byte 4
    #    9,  # 0x09      DIR Channel Status Ch2 Byte 4
    #    10, # 0x0A      DIR Channel Status Ch1 Byte 5
    #    11, # 0x0B      DIR Channel Status Ch2 Byte 5
    #    12, # 0x0C      DIR Channel Status Ch1 Byte 6
    #    13, # 0x0D      DIR Channel Status Ch2 Byte 6
    #    14, # 0x0E      DIR Channel Status Ch1 Byte 7
    #    15, # 0x0F      DIR Channel Status Ch2 Byte 7
    #    16, # 0x10      DIR Channel Status Ch1 Byte 8
    #    17, # 0x11      DIR Channel Status Ch2 Byte 8
    #    18, # 0x12      DIR Channel Status Ch1 Byte 9
    #    19, # 0x13      DIR Channel Status Ch2 Byte 9
    #    20, # 0x14      DIR Channel Status Ch1 Byte 10
    #    21, # 0x15      DIR Channel Status Ch2 Byte 10
    #    22, # 0x16      DIR Channel Status Ch1 Byte 11
    #    23, # 0x17      DIR Channel Status Ch2 Byte 11
    #    24, # 0x18      DIR Channel Status Ch1 Byte 12
    #    25, # 0x19      DIR Channel Status Ch2 Byte 12
    #    26, # 0x1A      DIR Channel Status Ch1 Byte 13
    #    27, # 0x1B      DIR Channel Status Ch2 Byte 13
    #    28, # 0x1C      DIR Channel Status Ch1 Byte 14
    #    29, # 0x1D      DIR Channel Status Ch2 Byte 14
    #    30, # 0x1E      DIR Channel Status Ch1 Byte 15
    #    31, # 0x1F      DIR Channel Status Ch2 Byte 15
    #    32, # 0x20      DIR Channel Status Ch1 Byte 16
    #    33, # 0x21      DIR Channel Status Ch2 Byte 16
    #    34, # 0x22      DIR Channel Status Ch1 Byte 17
    #    35, # 0x23      DIR Channel Status Ch2 Byte 17
    #    36, # 0x24      DIR Channel Status Ch1 Byte 18
    #    37, # 0x25      DIR Channel Status Ch2 Byte 18
    #    38, # 0x26      DIR Channel Status Ch1 Byte 19
    #    39, # 0x27      DIR Channel Status Ch2 Byte 19
    #    40, # 0x28      DIR Channel Status Ch1 Byte 20
    #    41, # 0x29      DIR Channel Status Ch2 Byte 20
    #    42, # 0x2A      DIR Channel Status Ch1 Byte 21
    #    43, # 0x2B      DIR Channel Status Ch2 Byte 21
    #    44, # 0x2C      DIR Channel Status Ch1 Byte 22
    #    45, # 0x2D      DIR Channel Status Ch2 Byte 22
    #    46, # 0x2E      DIR Channel Status Ch1 Byte 23
    #    47, # 0x2F      DIR Channel Status Ch2 Byte 23
    #    48, # 0x40      DIR User Data Ch2 Byte 0
    #    49, # 0x41      DIR User Data Ch1 Byte 0
    #    50, # 0x42      DIR User Data Ch2 Byte 1
    #    51, # 0x43      DIR User Data Ch1 Byte 1
    #    52, # 0x44      DIR User Data Ch2 Byte 2
    #    53, # 0x45      DIR User Data Ch1 Byte 2
    #    54, # 0x46      DIR User Data Ch2 Byte 3
    #    55, # 0x47      DIR User Data Ch1 Byte 3
    #    56, # 0x48      DIR User Data Ch2 Byte 4
    #    57, # 0x49      DIR User Data Ch1 Byte 4
    #    58, # 0x4A      DIR User Data Ch2 Byte 5
    #    59, # 0x4B      DIR User Data Ch1 Byte 5
    #    60, # 0x4C      DIR User Data Ch2 Byte 6
    #    61, # 0x4D      DIR User Data Ch1 Byte 6
    #    62, # 0x4E      DIR User Data Ch2 Byte 7
    #    63, # 0x4F      DIR User Data Ch1 Byte 7
    #    64, # 0x50      DIR User Data Ch2 Byte 8
    #    65, # 0x51      DIR User Data Ch1 Byte 8
    #    66, # 0x52      DIR User Data Ch2 Byte 9
    #    67, # 0x53      DIR User Data Ch1 Byte 9
    #    68, # 0x54      DIR User Data Ch2 Byte 10
    #    69, # 0x55      DIR User Data Ch1 Byte 10
    #    70, # 0x56      DIR User Data Ch2 Byte 11
    #    71, # 0x57      DIR User Data Ch1 Byte 11
    #    72, # 0x58      DIR User Data Ch2 Byte 12
    #    73, # 0x59      DIR User Data Ch1 Byte 12
    #    74, # 0x5A      DIR User Data Ch2 Byte 13
    #    75, # 0x5B      DIR User Data Ch1 Byte 13
    #    76, # 0x5C      DIR User Data Ch2 Byte 14
    #    77, # 0x5D      DIR User Data Ch1 Byte 14
    #    78, # 0x5E      DIR User Data Ch2 Byte 15
    #    79, # 0x5F      DIR User Data Ch1 Byte 15
    #    80, # 0x60      DIR User Data Ch2 Byte 16
    #    81, # 0x61      DIR User Data Ch1 Byte 16
    #    82, # 0x62      DIR User Data Ch2 Byte 17
    #    83, # 0x63      DIR User Data Ch1 Byte 17
    #    84, # 0x64      DIR User Data Ch2 Byte 18
    #    85, # 0x65      DIR User Data Ch1 Byte 18
    #    86, # 0x66      DIR User Data Ch2 Byte 19
    #    87, # 0x67      DIR User Data Ch1 Byte 19
    #    88, # 0x68      DIR User Data Ch2 Byte 20
    #    89, # 0x69      DIR User Data Ch1 Byte 20
    #    90, # 0x6A      DIR User Data Ch2 Byte 21
    #    91, # 0x6B      DIR User Data Ch1 Byte 21
    #    92, # 0x6C      DIR User Data Ch2 Byte 22
    #    93, # 0x6D      DIR User Data Ch2 Byte 22
    #    94, # 0x6E      DIR User Data Ch1 Byte 23
    #    95, # 0x6F      DIR User Data Ch2 Byte 23
    ]
    p2_reglist = [
        0,  # 0x00      DIT Channel Status Ch1 Byte 0
        1,  # 0x01      DIT Channel Status Ch2 Byte 0
        2,  # 0x02      DIT Channel Status Ch1 Byte 1
        3,  # 0x03      DIT Channel Status Ch2 Byte 1
        4,  # 0x04      DIT Channel Status Ch1 Byte 2
        5,  # 0x05      DIT Channel Status Ch2 Byte 2
        6,  # 0x06      DIT Channel Status Ch1 Byte 3
        7,  # 0x07      DIT Channel Status Ch2 Byte 3
    #    8,  # 0x08      DIT Channel Status Ch1 Byte 4
    #    9,  # 0x09      DIT Channel Status Ch2 Byte 4
    #    10, # 0x0A      DIT Channel Status Ch1 Byte 5
    #    11, # 0x0B      DIT Channel Status Ch2 Byte 5
    #    12, # 0x0C      DIT Channel Status Ch1 Byte 6
    #    13, # 0x0D      DIT Channel Status Ch2 Byte 6
    #    14, # 0x0E      DIT Channel Status Ch1 Byte 7
    #    15, # 0x0F      DIT Channel Status Ch2 Byte 7
    #    16, # 0x10      DIT Channel Status Ch1 Byte 8
    #    17, # 0x11      DIT Channel Status Ch2 Byte 8
    #    18, # 0x12      DIT Channel Status Ch1 Byte 9
    #    19, # 0x13      DIT Channel Status Ch2 Byte 9
    #    20, # 0x14      DIT Channel Status Ch1 Byte 10
    #    21, # 0x15      DIT Channel Status Ch2 Byte 10
    #    22, # 0x16      DIT Channel Status Ch1 Byte 11
    #    23, # 0x17      DIT Channel Status Ch2 Byte 11
    #    24, # 0x18      DIT Channel Status Ch1 Byte 12
    #    25, # 0x19      DIT Channel Status Ch2 Byte 12
    #    26, # 0x1A      DIT Channel Status Ch1 Byte 13
    #    27, # 0x1B      DIT Channel Status Ch2 Byte 13
    #    28, # 0x1C      DIT Channel Status Ch1 Byte 14
    #    29, # 0x1D      DIT Channel Status Ch2 Byte 14
    #    30, # 0x1E      DIT Channel Status Ch1 Byte 15
    #    31, # 0x1F      DIT Channel Status Ch2 Byte 15
    #    32, # 0x20      DIT Channel Status Ch1 Byte 16
    #    33, # 0x21      DIT Channel Status Ch2 Byte 16
    #    34, # 0x22      DIT Channel Status Ch1 Byte 17
    #    35, # 0x23      DIT Channel Status Ch2 Byte 17
    #    36, # 0x24      DIT Channel Status Ch1 Byte 18
    #    37, # 0x25      DIT Channel Status Ch2 Byte 18
    #    38, # 0x26      DIT Channel Status Ch1 Byte 19
    #    39, # 0x27      DIT Channel Status Ch2 Byte 19
    #    40, # 0x28      DIT Channel Status Ch1 Byte 20
    #    41, # 0x29      DIT Channel Status Ch2 Byte 20
    #    42, # 0x2A      DIT Channel Status Ch1 Byte 21
    #    43, # 0x2B      DIT Channel Status Ch2 Byte 21
    #    44, # 0x2C      DIT Channel Status Ch1 Byte 22
    #    45, # 0x2D      DIT Channel Status Ch2 Byte 22
    #    46, # 0x2E      DIT Channel Status Ch1 Byte 23
    #    47, # 0x2F      DIT Channel Status Ch2 Byte 23
    #    48, # 0x40      DIT User Data Ch2 Byte 0
    #    49, # 0x41      DIT User Data Ch1 Byte 0
    #    50, # 0x42      DIT User Data Ch2 Byte 1
    #    51, # 0x43      DIT User Data Ch1 Byte 1
    #    52, # 0x44      DIT User Data Ch2 Byte 2
    #    53, # 0x45      DIT User Data Ch1 Byte 2
    #    54, # 0x46      DIT User Data Ch2 Byte 3
    #    55, # 0x47      DIT User Data Ch1 Byte 3
    #    56, # 0x48      DIT User Data Ch2 Byte 4
    #    57, # 0x49      DIT User Data Ch1 Byte 4
    #    58, # 0x4A      DIT User Data Ch2 Byte 5
    #    59, # 0x4B      DIT User Data Ch1 Byte 5
    #    60, # 0x4C      DIT User Data Ch2 Byte 6
    #    61, # 0x4D      DIT User Data Ch1 Byte 6
    #    62, # 0x4E      DIT User Data Ch2 Byte 7
    #    63, # 0x4F      DIT User Data Ch1 Byte 7
    #    64, # 0x50      DIT User Data Ch2 Byte 8
    #    65, # 0x51      DIT User Data Ch1 Byte 8
    #    66, # 0x52      DIT User Data Ch2 Byte 9
    #    67, # 0x53      DIT User Data Ch1 Byte 9
    #    68, # 0x54      DIT User Data Ch2 Byte 10
    #    69, # 0x55      DIT User Data Ch1 Byte 10
    #    70, # 0x56      DIT User Data Ch2 Byte 11
    #    71, # 0x57      DIT User Data Ch1 Byte 11
    #    72, # 0x58      DIT User Data Ch2 Byte 12
    #    73, # 0x59      DIT User Data Ch1 Byte 12
    #    74, # 0x5A      DIT User Data Ch2 Byte 13
    #    75, # 0x5B      DIT User Data Ch1 Byte 13
    #    76, # 0x5C      DIT User Data Ch2 Byte 14
    #    77, # 0x5D      DIT User Data Ch1 Byte 14
    #    78, # 0x5E      DIR User Data Ch2 Byte 15
    #    79, # 0x5F      DIT User Data Ch1 Byte 15
    #    80, # 0x60      DIT User Data Ch2 Byte 16
    #    81, # 0x61      DIT User Data Ch1 Byte 16
    #    82, # 0x62      DIT User Data Ch2 Byte 17
    #    83, # 0x63      DIT User Data Ch1 Byte 17
    #    84, # 0x64      DIT User Data Ch2 Byte 18
    #    85, # 0x65      DIT User Data Ch1 Byte 18
    #    86, # 0x66      DIT User Data Ch2 Byte 19
    #    87, # 0x67      DIT User Data Ch1 Byte 19
    #    88, # 0x68      DIT User Data Ch2 Byte 20
    #    89, # 0x69      DIT User Data Ch1 Byte 20
    #    90, # 0x6A      DIT User Data Ch2 Byte 21
    #    91, # 0x6B      DIT User Data Ch1 Byte 21
    #    92, # 0x6C      DIT User Data Ch2 Byte 22
    #    93, # 0x6D      DIT User Data Ch2 Byte 22
    #    94, # 0x6E      DIT User Data Ch1 Byte 23
    #    95, # 0x6F      DIT User Data Ch2 Byte 23
    ]
elif chan == "I3":
    dev = "/dev/i2c-12"
    p0_reglist = [
        0,  # 0x01      Power-Down and Reset
    #    1,  # 0x02      Global Interrupt Status
        2,  # 0x03      Port A Control
        3,  # 0x04      Port A Control
    #    4,  # 0x05      Port B Control
    #    5,  # 0x06      Port B Control
    #    6,  # 0x07      Transmitter Control
    #    7,  # 0x08      Transmitter Control
    #    8,  # 0x09      Transmitter Control
        9,  # 0x0A      SRC and DIT Status
    #    10, # 0x0B      SRC and DIT Interrupt Mask
    #    11, # 0x0C      SRC and DIT Interrupt Mask
        12, # 0x0D      Receiver Control
        13, # 0x0E      Receiver Control
        14, # 0x0F-0x11 Receiver PLL Configuration
        15, # 0x12      Non-PCM Audio Detection
        16, # 0x13      Receiver Status
        17, # 0x14      Receiver Status
        18, # 0x15      Receiver Status
    #    19, # 0x16      Receiver Interrupt Mask
    #    20, # 0x17      Receiver Interrupt Mask
    #    21, # 0x18      Receiver Interrupt Mode
    #    22, # 0x19      Receiver Interrupt Mode
    #    23, # 0x1A      Receiver Interrupt Mode
    #    24, # 0x1B      General-Purpose Out (GPO1)
    #    25, # 0x1C      General-Purpose Out (GPO2)
    #    26, # 0x1D      General-Purpose Out (GPO3)
    #    27, # 0x1E      General-Purpose Out (GPO4)
    #    28, # 0x1F      Audio CD Q-Channel Sub-Code
    #    29, # 0x20      Audio CD Q-Channel Sub-Code
    #    30, # 0x21      Audio CD Q-Channel Sub-Code
    #    31, # 0x22      Audio CD Q-Channel Sub-Code
    #    32, # 0x23      Audio CD Q-Channel Sub-Code
    #    33, # 0x24      Audio CD Q-Channel Sub-Code
    #    34, # 0x25      Audio CD Q-Channel Sub-Code
    #    35, # 0x26      Audio CD Q-Channel Sub-Code
    #    36, # 0x27      Audio CD Q-Channel Sub-Code
    #    37, # 0x28      Audio CD Q-Channel Sub-Code
    #    38, # 0x29-0x2A PC Burst Preamble
    #    39, # 0x2B-0x2C PD Burst Preamble
        40, # 0x2D      SRC Control
        41, # 0x2E      SRC Control
        42, # 0x2F      SRC Control
        43, # 0x30      SRC Control Right Attenuation
        44, # 0x31      SRC Control Left Attenuation
        45, # 0x32-0x33 SRC Input: Output Ratio
    ]
    p1_reglist = [
        0,  # 0x00      DIR Channel Status Ch1 Byte 0
        1,  # 0x01      DIR Channel Status Ch2 Byte 0
        2,  # 0x02      DIR Channel Status Ch1 Byte 1
        3,  # 0x03      DIR Channel Status Ch2 Byte 1
        4,  # 0x04      DIR Channel Status Ch1 Byte 2
        5,  # 0x05      DIR Channel Status Ch2 Byte 2
        6,  # 0x06      DIR Channel Status Ch1 Byte 3
        7,  # 0x07      DIR Channel Status Ch2 Byte 3
    #    8,  # 0x08      DIR Channel Status Ch1 Byte 4
    #    9,  # 0x09      DIR Channel Status Ch2 Byte 4
    #    10, # 0x0A      DIR Channel Status Ch1 Byte 5
    #    11, # 0x0B      DIR Channel Status Ch2 Byte 5
    #    12, # 0x0C      DIR Channel Status Ch1 Byte 6
    #    13, # 0x0D      DIR Channel Status Ch2 Byte 6
    #    14, # 0x0E      DIR Channel Status Ch1 Byte 7
    #    15, # 0x0F      DIR Channel Status Ch2 Byte 7
    #    16, # 0x10      DIR Channel Status Ch1 Byte 8
    #    17, # 0x11      DIR Channel Status Ch2 Byte 8
    #    18, # 0x12      DIR Channel Status Ch1 Byte 9
    #    19, # 0x13      DIR Channel Status Ch2 Byte 9
    #    20, # 0x14      DIR Channel Status Ch1 Byte 10
    #    21, # 0x15      DIR Channel Status Ch2 Byte 10
    #    22, # 0x16      DIR Channel Status Ch1 Byte 11
    #    23, # 0x17      DIR Channel Status Ch2 Byte 11
    #    24, # 0x18      DIR Channel Status Ch1 Byte 12
    #    25, # 0x19      DIR Channel Status Ch2 Byte 12
    #    26, # 0x1A      DIR Channel Status Ch1 Byte 13
    #    27, # 0x1B      DIR Channel Status Ch2 Byte 13
    #    28, # 0x1C      DIR Channel Status Ch1 Byte 14
    #    29, # 0x1D      DIR Channel Status Ch2 Byte 14
    #    30, # 0x1E      DIR Channel Status Ch1 Byte 15
    #    31, # 0x1F      DIR Channel Status Ch2 Byte 15
    #    32, # 0x20      DIR Channel Status Ch1 Byte 16
    #    33, # 0x21      DIR Channel Status Ch2 Byte 16
    #    34, # 0x22      DIR Channel Status Ch1 Byte 17
    #    35, # 0x23      DIR Channel Status Ch2 Byte 17
    #    36, # 0x24      DIR Channel Status Ch1 Byte 18
    #    37, # 0x25      DIR Channel Status Ch2 Byte 18
    #    38, # 0x26      DIR Channel Status Ch1 Byte 19
    #    39, # 0x27      DIR Channel Status Ch2 Byte 19
    #    40, # 0x28      DIR Channel Status Ch1 Byte 20
    #    41, # 0x29      DIR Channel Status Ch2 Byte 20
    #    42, # 0x2A      DIR Channel Status Ch1 Byte 21
    #    43, # 0x2B      DIR Channel Status Ch2 Byte 21
    #    44, # 0x2C      DIR Channel Status Ch1 Byte 22
    #    45, # 0x2D      DIR Channel Status Ch2 Byte 22
    #    46, # 0x2E      DIR Channel Status Ch1 Byte 23
    #    47, # 0x2F      DIR Channel Status Ch2 Byte 23
    #    48, # 0x40      DIR User Data Ch2 Byte 0
    #    49, # 0x41      DIR User Data Ch1 Byte 0
    #    50, # 0x42      DIR User Data Ch2 Byte 1
    #    51, # 0x43      DIR User Data Ch1 Byte 1
    #    52, # 0x44      DIR User Data Ch2 Byte 2
    #    53, # 0x45      DIR User Data Ch1 Byte 2
    #    54, # 0x46      DIR User Data Ch2 Byte 3
    #    55, # 0x47      DIR User Data Ch1 Byte 3
    #    56, # 0x48      DIR User Data Ch2 Byte 4
    #    57, # 0x49      DIR User Data Ch1 Byte 4
    #    58, # 0x4A      DIR User Data Ch2 Byte 5
    #    59, # 0x4B      DIR User Data Ch1 Byte 5
    #    60, # 0x4C      DIR User Data Ch2 Byte 6
    #    61, # 0x4D      DIR User Data Ch1 Byte 6
    #    62, # 0x4E      DIR User Data Ch2 Byte 7
    #    63, # 0x4F      DIR User Data Ch1 Byte 7
    #    64, # 0x50      DIR User Data Ch2 Byte 8
    #    65, # 0x51      DIR User Data Ch1 Byte 8
    #    66, # 0x52      DIR User Data Ch2 Byte 9
    #    67, # 0x53      DIR User Data Ch1 Byte 9
    #    68, # 0x54      DIR User Data Ch2 Byte 10
    #    69, # 0x55      DIR User Data Ch1 Byte 10
    #    70, # 0x56      DIR User Data Ch2 Byte 11
    #    71, # 0x57      DIR User Data Ch1 Byte 11
    #    72, # 0x58      DIR User Data Ch2 Byte 12
    #    73, # 0x59      DIR User Data Ch1 Byte 12
    #    74, # 0x5A      DIR User Data Ch2 Byte 13
    #    75, # 0x5B      DIR User Data Ch1 Byte 13
    #    76, # 0x5C      DIR User Data Ch2 Byte 14
    #    77, # 0x5D      DIR User Data Ch1 Byte 14
    #    78, # 0x5E      DIR User Data Ch2 Byte 15
    #    79, # 0x5F      DIR User Data Ch1 Byte 15
    #    80, # 0x60      DIR User Data Ch2 Byte 16
    #    81, # 0x61      DIR User Data Ch1 Byte 16
    #    82, # 0x62      DIR User Data Ch2 Byte 17
    #    83, # 0x63      DIR User Data Ch1 Byte 17
    #    84, # 0x64      DIR User Data Ch2 Byte 18
    #    85, # 0x65      DIR User Data Ch1 Byte 18
    #    86, # 0x66      DIR User Data Ch2 Byte 19
    #    87, # 0x67      DIR User Data Ch1 Byte 19
    #    88, # 0x68      DIR User Data Ch2 Byte 20
    #    89, # 0x69      DIR User Data Ch1 Byte 20
    #    90, # 0x6A      DIR User Data Ch2 Byte 21
    #    91, # 0x6B      DIR User Data Ch1 Byte 21
    #    92, # 0x6C      DIR User Data Ch2 Byte 22
    #    93, # 0x6D      DIR User Data Ch2 Byte 22
    #    94, # 0x6E      DIR User Data Ch1 Byte 23
    #    95, # 0x6F      DIR User Data Ch2 Byte 23
    ]
    p2_reglist = [
    #    0,  # 0x00      DIT Channel Status Ch1 Byte 0
    #    1,  # 0x01      DIT Channel Status Ch2 Byte 0
    #    2,  # 0x02      DIT Channel Status Ch1 Byte 1
    #    3,  # 0x03      DIT Channel Status Ch2 Byte 1
    #    4,  # 0x04      DIT Channel Status Ch1 Byte 2
    #    5,  # 0x05      DIT Channel Status Ch2 Byte 2
    #    6,  # 0x06      DIT Channel Status Ch1 Byte 3
    #    7,  # 0x07      DIT Channel Status Ch2 Byte 3
    #    8,  # 0x08      DIT Channel Status Ch1 Byte 4
    #    9,  # 0x09      DIT Channel Status Ch2 Byte 4
    #    10, # 0x0A      DIT Channel Status Ch1 Byte 5
    #    11, # 0x0B      DIT Channel Status Ch2 Byte 5
    #    12, # 0x0C      DIT Channel Status Ch1 Byte 6
    #    13, # 0x0D      DIT Channel Status Ch2 Byte 6
    #    14, # 0x0E      DIT Channel Status Ch1 Byte 7
    #    15, # 0x0F      DIT Channel Status Ch2 Byte 7
    #    16, # 0x10      DIT Channel Status Ch1 Byte 8
    #    17, # 0x11      DIT Channel Status Ch2 Byte 8
    #    18, # 0x12      DIT Channel Status Ch1 Byte 9
    #    19, # 0x13      DIT Channel Status Ch2 Byte 9
    #    20, # 0x14      DIT Channel Status Ch1 Byte 10
    #    21, # 0x15      DIT Channel Status Ch2 Byte 10
    #    22, # 0x16      DIT Channel Status Ch1 Byte 11
    #    23, # 0x17      DIT Channel Status Ch2 Byte 11
    #    24, # 0x18      DIT Channel Status Ch1 Byte 12
    #    25, # 0x19      DIT Channel Status Ch2 Byte 12
    #    26, # 0x1A      DIT Channel Status Ch1 Byte 13
    #    27, # 0x1B      DIT Channel Status Ch2 Byte 13
    #    28, # 0x1C      DIT Channel Status Ch1 Byte 14
    #    29, # 0x1D      DIT Channel Status Ch2 Byte 14
    #    30, # 0x1E      DIT Channel Status Ch1 Byte 15
    #    31, # 0x1F      DIT Channel Status Ch2 Byte 15
    #    32, # 0x20      DIT Channel Status Ch1 Byte 16
    #    33, # 0x21      DIT Channel Status Ch2 Byte 16
    #    34, # 0x22      DIT Channel Status Ch1 Byte 17
    #    35, # 0x23      DIT Channel Status Ch2 Byte 17
    #    36, # 0x24      DIT Channel Status Ch1 Byte 18
    #    37, # 0x25      DIT Channel Status Ch2 Byte 18
    #    38, # 0x26      DIT Channel Status Ch1 Byte 19
    #    39, # 0x27      DIT Channel Status Ch2 Byte 19
    #    40, # 0x28      DIT Channel Status Ch1 Byte 20
    #    41, # 0x29      DIT Channel Status Ch2 Byte 20
    #    42, # 0x2A      DIT Channel Status Ch1 Byte 21
    #    43, # 0x2B      DIT Channel Status Ch2 Byte 21
    #    44, # 0x2C      DIT Channel Status Ch1 Byte 22
    #    45, # 0x2D      DIT Channel Status Ch2 Byte 22
    #    46, # 0x2E      DIT Channel Status Ch1 Byte 23
    #    47, # 0x2F      DIT Channel Status Ch2 Byte 23
    #    48, # 0x40      DIT User Data Ch2 Byte 0
    #    49, # 0x41      DIT User Data Ch1 Byte 0
    #    50, # 0x42      DIT User Data Ch2 Byte 1
    #    51, # 0x43      DIT User Data Ch1 Byte 1
    #    52, # 0x44      DIT User Data Ch2 Byte 2
    #    53, # 0x45      DIT User Data Ch1 Byte 2
    #    54, # 0x46      DIT User Data Ch2 Byte 3
    #    55, # 0x47      DIT User Data Ch1 Byte 3
    #    56, # 0x48      DIT User Data Ch2 Byte 4
    #    57, # 0x49      DIT User Data Ch1 Byte 4
    #    58, # 0x4A      DIT User Data Ch2 Byte 5
    #    59, # 0x4B      DIT User Data Ch1 Byte 5
    #    60, # 0x4C      DIT User Data Ch2 Byte 6
    #    61, # 0x4D      DIT User Data Ch1 Byte 6
    #    62, # 0x4E      DIT User Data Ch2 Byte 7
    #    63, # 0x4F      DIT User Data Ch1 Byte 7
    #    64, # 0x50      DIT User Data Ch2 Byte 8
    #    65, # 0x51      DIT User Data Ch1 Byte 8
    #    66, # 0x52      DIT User Data Ch2 Byte 9
    #    67, # 0x53      DIT User Data Ch1 Byte 9
    #    68, # 0x54      DIT User Data Ch2 Byte 10
    #    69, # 0x55      DIT User Data Ch1 Byte 10
    #    70, # 0x56      DIT User Data Ch2 Byte 11
    #    71, # 0x57      DIT User Data Ch1 Byte 11
    #    72, # 0x58      DIT User Data Ch2 Byte 12
    #    73, # 0x59      DIT User Data Ch1 Byte 12
    #    74, # 0x5A      DIT User Data Ch2 Byte 13
    #    75, # 0x5B      DIT User Data Ch1 Byte 13
    #    76, # 0x5C      DIT User Data Ch2 Byte 14
    #    77, # 0x5D      DIT User Data Ch1 Byte 14
    #    78, # 0x5E      DIR User Data Ch2 Byte 15
    #    79, # 0x5F      DIT User Data Ch1 Byte 15
    #    80, # 0x60      DIT User Data Ch2 Byte 16
    #    81, # 0x61      DIT User Data Ch1 Byte 16
    #    82, # 0x62      DIT User Data Ch2 Byte 17
    #    83, # 0x63      DIT User Data Ch1 Byte 17
    #    84, # 0x64      DIT User Data Ch2 Byte 18
    #    85, # 0x65      DIT User Data Ch1 Byte 18
    #    86, # 0x66      DIT User Data Ch2 Byte 19
    #    87, # 0x67      DIT User Data Ch1 Byte 19
    #    88, # 0x68      DIT User Data Ch2 Byte 20
    #    89, # 0x69      DIT User Data Ch1 Byte 20
    #    90, # 0x6A      DIT User Data Ch2 Byte 21
    #    91, # 0x6B      DIT User Data Ch1 Byte 21
    #    92, # 0x6C      DIT User Data Ch2 Byte 22
    #    93, # 0x6D      DIT User Data Ch2 Byte 22
    #    94, # 0x6E      DIT User Data Ch1 Byte 23
    #    95, # 0x6F      DIT User Data Ch2 Byte 23
    ]
elif chan == "I4":
    dev = "/dev/i2c-13"
    p0_reglist = [
        0,  # 0x01      Power-Down and Reset
    #    1,  # 0x02      Global Interrupt Status
        2,  # 0x03      Port A Control
        3,  # 0x04      Port A Control
    #    4,  # 0x05      Port B Control
    #    5,  # 0x06      Port B Control
    #    6,  # 0x07      Transmitter Control
    #    7,  # 0x08      Transmitter Control
    #    8,  # 0x09      Transmitter Control
        9,  # 0x0A      SRC and DIT Status
    #    10, # 0x0B      SRC and DIT Interrupt Mask
    #    11, # 0x0C      SRC and DIT Interrupt Mask
        12, # 0x0D      Receiver Control
        13, # 0x0E      Receiver Control
        14, # 0x0F-0x11 Receiver PLL Configuration
        15, # 0x12      Non-PCM Audio Detection
        16, # 0x13      Receiver Status
        17, # 0x14      Receiver Status
        18, # 0x15      Receiver Status
    #    19, # 0x16      Receiver Interrupt Mask
    #    20, # 0x17      Receiver Interrupt Mask
    #    21, # 0x18      Receiver Interrupt Mode
    #    22, # 0x19      Receiver Interrupt Mode
    #    23, # 0x1A      Receiver Interrupt Mode
    #    24, # 0x1B      General-Purpose Out (GPO1)
    #    25, # 0x1C      General-Purpose Out (GPO2)
    #    26, # 0x1D      General-Purpose Out (GPO3)
    #    27, # 0x1E      General-Purpose Out (GPO4)
    #    28, # 0x1F      Audio CD Q-Channel Sub-Code
    #    29, # 0x20      Audio CD Q-Channel Sub-Code
    #    30, # 0x21      Audio CD Q-Channel Sub-Code
    #    31, # 0x22      Audio CD Q-Channel Sub-Code
    #    32, # 0x23      Audio CD Q-Channel Sub-Code
    #    33, # 0x24      Audio CD Q-Channel Sub-Code
    #    34, # 0x25      Audio CD Q-Channel Sub-Code
    #    35, # 0x26      Audio CD Q-Channel Sub-Code
    #    36, # 0x27      Audio CD Q-Channel Sub-Code
    #    37, # 0x28      Audio CD Q-Channel Sub-Code
    #    38, # 0x29-0x2A PC Burst Preamble
    #    39, # 0x2B-0x2C PD Burst Preamble
        40, # 0x2D      SRC Control
        41, # 0x2E      SRC Control
        42, # 0x2F      SRC Control
        43, # 0x30      SRC Control Right Attenuation
        44, # 0x31      SRC Control Left Attenuation
        45, # 0x32-0x33 SRC Input: Output Ratio
    ]
    p1_reglist = [
        0,  # 0x00      DIR Channel Status Ch1 Byte 0
        1,  # 0x01      DIR Channel Status Ch2 Byte 0
        2,  # 0x02      DIR Channel Status Ch1 Byte 1
        3,  # 0x03      DIR Channel Status Ch2 Byte 1
        4,  # 0x04      DIR Channel Status Ch1 Byte 2
        5,  # 0x05      DIR Channel Status Ch2 Byte 2
        6,  # 0x06      DIR Channel Status Ch1 Byte 3
        7,  # 0x07      DIR Channel Status Ch2 Byte 3
    #    8,  # 0x08      DIR Channel Status Ch1 Byte 4
    #    9,  # 0x09      DIR Channel Status Ch2 Byte 4
    #    10, # 0x0A      DIR Channel Status Ch1 Byte 5
    #    11, # 0x0B      DIR Channel Status Ch2 Byte 5
    #    12, # 0x0C      DIR Channel Status Ch1 Byte 6
    #    13, # 0x0D      DIR Channel Status Ch2 Byte 6
    #    14, # 0x0E      DIR Channel Status Ch1 Byte 7
    #    15, # 0x0F      DIR Channel Status Ch2 Byte 7
    #    16, # 0x10      DIR Channel Status Ch1 Byte 8
    #    17, # 0x11      DIR Channel Status Ch2 Byte 8
    #    18, # 0x12      DIR Channel Status Ch1 Byte 9
    #    19, # 0x13      DIR Channel Status Ch2 Byte 9
    #    20, # 0x14      DIR Channel Status Ch1 Byte 10
    #    21, # 0x15      DIR Channel Status Ch2 Byte 10
    #    22, # 0x16      DIR Channel Status Ch1 Byte 11
    #    23, # 0x17      DIR Channel Status Ch2 Byte 11
    #    24, # 0x18      DIR Channel Status Ch1 Byte 12
    #    25, # 0x19      DIR Channel Status Ch2 Byte 12
    #    26, # 0x1A      DIR Channel Status Ch1 Byte 13
    #    27, # 0x1B      DIR Channel Status Ch2 Byte 13
    #    28, # 0x1C      DIR Channel Status Ch1 Byte 14
    #    29, # 0x1D      DIR Channel Status Ch2 Byte 14
    #    30, # 0x1E      DIR Channel Status Ch1 Byte 15
    #    31, # 0x1F      DIR Channel Status Ch2 Byte 15
    #    32, # 0x20      DIR Channel Status Ch1 Byte 16
    #    33, # 0x21      DIR Channel Status Ch2 Byte 16
    #    34, # 0x22      DIR Channel Status Ch1 Byte 17
    #    35, # 0x23      DIR Channel Status Ch2 Byte 17
    #    36, # 0x24      DIR Channel Status Ch1 Byte 18
    #    37, # 0x25      DIR Channel Status Ch2 Byte 18
    #    38, # 0x26      DIR Channel Status Ch1 Byte 19
    #    39, # 0x27      DIR Channel Status Ch2 Byte 19
    #    40, # 0x28      DIR Channel Status Ch1 Byte 20
    #    41, # 0x29      DIR Channel Status Ch2 Byte 20
    #    42, # 0x2A      DIR Channel Status Ch1 Byte 21
    #    43, # 0x2B      DIR Channel Status Ch2 Byte 21
    #    44, # 0x2C      DIR Channel Status Ch1 Byte 22
    #    45, # 0x2D      DIR Channel Status Ch2 Byte 22
    #    46, # 0x2E      DIR Channel Status Ch1 Byte 23
    #    47, # 0x2F      DIR Channel Status Ch2 Byte 23
    #    48, # 0x40      DIR User Data Ch2 Byte 0
    #    49, # 0x41      DIR User Data Ch1 Byte 0
    #    50, # 0x42      DIR User Data Ch2 Byte 1
    #    51, # 0x43      DIR User Data Ch1 Byte 1
    #    52, # 0x44      DIR User Data Ch2 Byte 2
    #    53, # 0x45      DIR User Data Ch1 Byte 2
    #    54, # 0x46      DIR User Data Ch2 Byte 3
    #    55, # 0x47      DIR User Data Ch1 Byte 3
    #    56, # 0x48      DIR User Data Ch2 Byte 4
    #    57, # 0x49      DIR User Data Ch1 Byte 4
    #    58, # 0x4A      DIR User Data Ch2 Byte 5
    #    59, # 0x4B      DIR User Data Ch1 Byte 5
    #    60, # 0x4C      DIR User Data Ch2 Byte 6
    #    61, # 0x4D      DIR User Data Ch1 Byte 6
    #    62, # 0x4E      DIR User Data Ch2 Byte 7
    #    63, # 0x4F      DIR User Data Ch1 Byte 7
    #    64, # 0x50      DIR User Data Ch2 Byte 8
    #    65, # 0x51      DIR User Data Ch1 Byte 8
    #    66, # 0x52      DIR User Data Ch2 Byte 9
    #    67, # 0x53      DIR User Data Ch1 Byte 9
    #    68, # 0x54      DIR User Data Ch2 Byte 10
    #    69, # 0x55      DIR User Data Ch1 Byte 10
    #    70, # 0x56      DIR User Data Ch2 Byte 11
    #    71, # 0x57      DIR User Data Ch1 Byte 11
    #    72, # 0x58      DIR User Data Ch2 Byte 12
    #    73, # 0x59      DIR User Data Ch1 Byte 12
    #    74, # 0x5A      DIR User Data Ch2 Byte 13
    #    75, # 0x5B      DIR User Data Ch1 Byte 13
    #    76, # 0x5C      DIR User Data Ch2 Byte 14
    #    77, # 0x5D      DIR User Data Ch1 Byte 14
    #    78, # 0x5E      DIR User Data Ch2 Byte 15
    #    79, # 0x5F      DIR User Data Ch1 Byte 15
    #    80, # 0x60      DIR User Data Ch2 Byte 16
    #    81, # 0x61      DIR User Data Ch1 Byte 16
    #    82, # 0x62      DIR User Data Ch2 Byte 17
    #    83, # 0x63      DIR User Data Ch1 Byte 17
    #    84, # 0x64      DIR User Data Ch2 Byte 18
    #    85, # 0x65      DIR User Data Ch1 Byte 18
    #    86, # 0x66      DIR User Data Ch2 Byte 19
    #    87, # 0x67      DIR User Data Ch1 Byte 19
    #    88, # 0x68      DIR User Data Ch2 Byte 20
    #    89, # 0x69      DIR User Data Ch1 Byte 20
    #    90, # 0x6A      DIR User Data Ch2 Byte 21
    #    91, # 0x6B      DIR User Data Ch1 Byte 21
    #    92, # 0x6C      DIR User Data Ch2 Byte 22
    #    93, # 0x6D      DIR User Data Ch2 Byte 22
    #    94, # 0x6E      DIR User Data Ch1 Byte 23
    #    95, # 0x6F      DIR User Data Ch2 Byte 23
    ]
    p2_reglist = [
    #    0,  # 0x00      DIT Channel Status Ch1 Byte 0
    #    1,  # 0x01      DIT Channel Status Ch2 Byte 0
    #    2,  # 0x02      DIT Channel Status Ch1 Byte 1
    #    3,  # 0x03      DIT Channel Status Ch2 Byte 1
    #    4,  # 0x04      DIT Channel Status Ch1 Byte 2
    #    5,  # 0x05      DIT Channel Status Ch2 Byte 2
    #    6,  # 0x06      DIT Channel Status Ch1 Byte 3
    #    7,  # 0x07      DIT Channel Status Ch2 Byte 3
    #    8,  # 0x08      DIT Channel Status Ch1 Byte 4
    #    9,  # 0x09      DIT Channel Status Ch2 Byte 4
    #    10, # 0x0A      DIT Channel Status Ch1 Byte 5
    #    11, # 0x0B      DIT Channel Status Ch2 Byte 5
    #    12, # 0x0C      DIT Channel Status Ch1 Byte 6
    #    13, # 0x0D      DIT Channel Status Ch2 Byte 6
    #    14, # 0x0E      DIT Channel Status Ch1 Byte 7
    #    15, # 0x0F      DIT Channel Status Ch2 Byte 7
    #    16, # 0x10      DIT Channel Status Ch1 Byte 8
    #    17, # 0x11      DIT Channel Status Ch2 Byte 8
    #    18, # 0x12      DIT Channel Status Ch1 Byte 9
    #    19, # 0x13      DIT Channel Status Ch2 Byte 9
    #    20, # 0x14      DIT Channel Status Ch1 Byte 10
    #    21, # 0x15      DIT Channel Status Ch2 Byte 10
    #    22, # 0x16      DIT Channel Status Ch1 Byte 11
    #    23, # 0x17      DIT Channel Status Ch2 Byte 11
    #    24, # 0x18      DIT Channel Status Ch1 Byte 12
    #    25, # 0x19      DIT Channel Status Ch2 Byte 12
    #    26, # 0x1A      DIT Channel Status Ch1 Byte 13
    #    27, # 0x1B      DIT Channel Status Ch2 Byte 13
    #    28, # 0x1C      DIT Channel Status Ch1 Byte 14
    #    29, # 0x1D      DIT Channel Status Ch2 Byte 14
    #    30, # 0x1E      DIT Channel Status Ch1 Byte 15
    #    31, # 0x1F      DIT Channel Status Ch2 Byte 15
    #    32, # 0x20      DIT Channel Status Ch1 Byte 16
    #    33, # 0x21      DIT Channel Status Ch2 Byte 16
    #    34, # 0x22      DIT Channel Status Ch1 Byte 17
    #    35, # 0x23      DIT Channel Status Ch2 Byte 17
    #    36, # 0x24      DIT Channel Status Ch1 Byte 18
    #    37, # 0x25      DIT Channel Status Ch2 Byte 18
    #    38, # 0x26      DIT Channel Status Ch1 Byte 19
    #    39, # 0x27      DIT Channel Status Ch2 Byte 19
    #    40, # 0x28      DIT Channel Status Ch1 Byte 20
    #    41, # 0x29      DIT Channel Status Ch2 Byte 20
    #    42, # 0x2A      DIT Channel Status Ch1 Byte 21
    #    43, # 0x2B      DIT Channel Status Ch2 Byte 21
    #    44, # 0x2C      DIT Channel Status Ch1 Byte 22
    #    45, # 0x2D      DIT Channel Status Ch2 Byte 22
    #    46, # 0x2E      DIT Channel Status Ch1 Byte 23
    #    47, # 0x2F      DIT Channel Status Ch2 Byte 23
    #    48, # 0x40      DIT User Data Ch2 Byte 0
    #    49, # 0x41      DIT User Data Ch1 Byte 0
    #    50, # 0x42      DIT User Data Ch2 Byte 1
    #    51, # 0x43      DIT User Data Ch1 Byte 1
    #    52, # 0x44      DIT User Data Ch2 Byte 2
    #    53, # 0x45      DIT User Data Ch1 Byte 2
    #    54, # 0x46      DIT User Data Ch2 Byte 3
    #    55, # 0x47      DIT User Data Ch1 Byte 3
    #    56, # 0x48      DIT User Data Ch2 Byte 4
    #    57, # 0x49      DIT User Data Ch1 Byte 4
    #    58, # 0x4A      DIT User Data Ch2 Byte 5
    #    59, # 0x4B      DIT User Data Ch1 Byte 5
    #    60, # 0x4C      DIT User Data Ch2 Byte 6
    #    61, # 0x4D      DIT User Data Ch1 Byte 6
    #    62, # 0x4E      DIT User Data Ch2 Byte 7
    #    63, # 0x4F      DIT User Data Ch1 Byte 7
    #    64, # 0x50      DIT User Data Ch2 Byte 8
    #    65, # 0x51      DIT User Data Ch1 Byte 8
    #    66, # 0x52      DIT User Data Ch2 Byte 9
    #    67, # 0x53      DIT User Data Ch1 Byte 9
    #    68, # 0x54      DIT User Data Ch2 Byte 10
    #    69, # 0x55      DIT User Data Ch1 Byte 10
    #    70, # 0x56      DIT User Data Ch2 Byte 11
    #    71, # 0x57      DIT User Data Ch1 Byte 11
    #    72, # 0x58      DIT User Data Ch2 Byte 12
    #    73, # 0x59      DIT User Data Ch1 Byte 12
    #    74, # 0x5A      DIT User Data Ch2 Byte 13
    #    75, # 0x5B      DIT User Data Ch1 Byte 13
    #    76, # 0x5C      DIT User Data Ch2 Byte 14
    #    77, # 0x5D      DIT User Data Ch1 Byte 14
    #    78, # 0x5E      DIR User Data Ch2 Byte 15
    #    79, # 0x5F      DIT User Data Ch1 Byte 15
    #    80, # 0x60      DIT User Data Ch2 Byte 16
    #    81, # 0x61      DIT User Data Ch1 Byte 16
    #    82, # 0x62      DIT User Data Ch2 Byte 17
    #    83, # 0x63      DIT User Data Ch1 Byte 17
    #    84, # 0x64      DIT User Data Ch2 Byte 18
    #    85, # 0x65      DIT User Data Ch1 Byte 18
    #    86, # 0x66      DIT User Data Ch2 Byte 19
    #    87, # 0x67      DIT User Data Ch1 Byte 19
    #    88, # 0x68      DIT User Data Ch2 Byte 20
    #    89, # 0x69      DIT User Data Ch1 Byte 20
    #    90, # 0x6A      DIT User Data Ch2 Byte 21
    #    91, # 0x6B      DIT User Data Ch1 Byte 21
    #    92, # 0x6C      DIT User Data Ch2 Byte 22
    #    93, # 0x6D      DIT User Data Ch2 Byte 22
    #    94, # 0x6E      DIT User Data Ch1 Byte 23
    #    95, # 0x6F      DIT User Data Ch2 Byte 23
    ]
else:
    print("Unknown channel")
    sys.exit()

i2c=I2C(dev)

p0_regs = {}
p1_regs = {}
p2_regs = {}

i2c_reg_write(i2c, 0x70, 0x7F, 0x00)  # page 0
for i in p0_reglist:
    p0_regs[src4392_page0[i]["name"]] = reg_decode(i2c, 0x70, src4392_page0[i])

i2c_reg_write(i2c, 0x70, 0x7F, 0x01)  # page 1
for i in p1_reglist:
    p2_regs[src4392_page1[i]["name"]] = reg_decode(i2c, 0x70, src4392_page1[i])

i2c_reg_write(i2c, 0x70, 0x7F, 0x02)  # page 2
for i in p2_reglist:
    p2_regs[src4392_page2[i]["name"]] = reg_decode(i2c, 0x70, src4392_page2[i])

i2c_reg_write(i2c, 0x70, 0x7F, 0x00)  # page 0

i2c.close()

pdict(p0_regs)
pdict(p1_regs)
pdict(p2_regs)
