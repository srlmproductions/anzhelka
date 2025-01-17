''********************************************
''*  This is a modified version of FDS that  *
''*  uses buffer sizes based on the constatn *
''*  buff_size.  It also has the new methods *
''*  txbuffer and txchunk to provide higher  *
''*  data transmit speeds.                   *
''********************************************
''*  Full-Duplex Serial Driver v1.2          *
''*  Author: Chip Gracey, Jeff Martin        *
''*  Copyright (c) 2006-2009 Parallax, Inc.  *
''*  See end of file for terms of use.       *
''********************************************

{-----------------REVISION HISTORY-----------------
 v1.2 - 5/7/2009 fixed bug in dec method causing largest negative value (-2,147,483,648) to be output as -0.
 v1.1 - 3/1/2006 first official release.
} 

CON
  buff_size = 256
  buff_mask = buff_size - 1

VAR

  long  cog                     'cog flag/id

  long  rx_head                 '9 contiguous longs
  long  rx_tail
  long  tx_head
  long  tx_tail
  long  rx_pin
  long  tx_pin
  long  rxtx_mode
  long  bit_ticks
  long  buffer_ptr
                     
  byte  rx_buffer[buff_mask+1]           'transmit and receive buffers
  byte  tx_buffer[buff_mask+1]  


PUB start(rxpin, txpin, mode, baudrate) : okay

'' Start serial driver - starts a cog
'' returns false if no cog available
''
'' mode bit 0 = invert rx
'' mode bit 1 = invert tx
'' mode bit 2 = open-drain/source tx
'' mode bit 3 = ignore tx echo on rx

  stop
  longfill(@rx_head, 0, 4)
  longmove(@rx_pin, @rxpin, 3)
  bit_ticks := clkfreq / baudrate
  buffer_ptr := @rx_buffer
  okay := cog := cognew(@entry, @rx_head) + 1


PUB stop

'' Stop serial driver - frees a cog

  if cog
    cogstop(cog~ - 1)
  longfill(@rx_head, 0, 9)


PUB rxflush

'' Flush receive buffer

  repeat while rxcheck => 0
  
    
PUB rxcheck : rxbyte

'' Check if byte received (never waits)
'' returns -1 if no byte received, $00..$FF if byte

  rxbyte--
  if rx_tail <> rx_head
    rxbyte := rx_buffer[rx_tail]
    rx_tail := (rx_tail + 1) & buff_mask


PUB rxtime(ms) : rxbyte | t

'' Wait ms milliseconds for a byte to be received
'' returns -1 if no byte received, $00..$FF if byte

  t := cnt
  repeat until (rxbyte := rxcheck) => 0 or (cnt - t) / (clkfreq / 1000) > ms
  

PUB rx : rxbyte

'' Receive byte (may wait for byte)
'' returns $00..$FF

  repeat
  while (rxbyte := rxcheck) < 0

PUB rxpeek : rxbyte
'' Receives byte without removing from buffer (may wait for byte
'' return $00..$FF
  repeat while rx_tail == rx_head
     
  rxbyte := rx_buffer[rx_tail]



PUB tx(txbyte)

'' Send byte (may wait for room in buffer)

  repeat
  until (tx_tail <> (tx_head + 1) & buff_mask)
  tx_buffer[tx_head] := txbyte
  tx_head := (tx_head + 1) & buff_mask

'  if rxtx_mode & %1000 'TODO: Make note that this is removed
'    rx


PUB str(stringptr)

'' Send string                    

  repeat strsize(stringptr)
    tx(byte[stringptr++])

PUB getstr(stringptr, terminator) | index
    '' Gets "terminator" terminated or newline (Ascii 13) terminated string and stores it, starting at the stringptr memory address
    index~
    repeat until ((byte[stringptr][index++] := rx) == terminator or byte[stringptr][index-1] == 13 or byte[stringptr][index-1] == 10)
    byte[stringptr][--index]~   

PUB dec(value) | i, x

'' Print a decimal number

  x := value == NEGX                                                            'Check for max negative
  if value < 0
    value := ||(value+x)                                                        'If negative, make positive; adjust for max negative
    tx("-")                                                                     'and output sign

  i := 1_000_000_000                                                            'Initialize divisor

  repeat 10                                                                     'Loop for 10 digits
    if value => i                                                               
      tx(value / i + "0" + x*(i == 1))                                          'If non-zero digit, output digit; adjust for max negative
      value //= i                                                               'and digit from value
      result~~                                                                  'flag non-zero found
    elseif result or i == 1
      tx("0")                                                                   'If zero digit (or only digit) output it
    i /= 10                                                                     'Update divisor

PUB GetDec(terminator) : value | tempstr[11]

    '' Gets decimal character representation of a number from the terminal
    '' Returns the corresponding value

    GetStr(@tempstr, terminator)
    value := StrToDec(@tempstr)    

PUB StrToDec(stringptr) : value | char, index, multiply

    '' Converts a zero terminated string representation of a decimal number to a value

    value := index := 0
    repeat until ((char := byte[stringptr][index++]) == 0)
       if char => "0" and char =< "9"
          value := value * 10 + (char - "0")
    if byte[stringptr] == "-"
       value := - value
       
       
PUB hex(value, digits)

'' Print a hexadecimal number

  value <<= (8 - digits) << 2
  repeat digits
    tx(lookupz((value <-= 4) & $F : "0".."9", "A".."F"))

PUB GetHex(terminator) : value | tempstr[11]

    '' Gets hexadecimal character representation of a number from the terminal
    '' Returns the corresponding value

    GetStr(@tempstr, terminator)
    value := StrToHex(@tempstr)    

PUB StrToHex(stringptr) : value | char, index

    '' Converts a zero terminated string representaton of a hexadecimal number to a value

    value := index := 0
    repeat until ((char := byte[stringptr][index++]) == 0)
       if (char => "0" and char =< "9")
          value := value * 16 + (char - "0")
       elseif (char => "A" and char =< "F")
          value := value * 16 + (10 + char - "A")
       elseif(char => "a" and char =< "f")   
          value := value * 16 + (10 + char - "a")
    if byte[stringptr] == "-"
       value := - value

PUB bin(value, digits)

'' Print a binary number

  value <<= 32 - digits
  repeat digits
    tx((value <-= 1) & 1 + "0")
    
PUB GetBin(terminator) : value | tempstr[11]

  '' Gets binary character representation of a number from the terminal
  '' Returns the corresponding value
   
  GetStr(@tempstr, terminator)
  value := StrToBin(@tempstr)    
   
PUB StrToBin(stringptr) : value | char, index

  '' Converts a zero terminated string representaton of a binary number to a value
   
  value := index := 0
  repeat until ((char := byte[stringptr][index++]) == 0)
     if char => "0" and char =< "1"
        value := value * 2 + (char - "0")
  if byte[stringptr] == "-"
     value := - value

PUB txblock(ptr, num) | num1
'Call this method (not txchunk)
  repeat while num > 0
    num1 := txchunk(ptr, num)
    num -= num1
    ptr += num1

PRI txchunk(ptr, num) | num1, num2, wrapnum
  ifnot (num1 := (tx_tail - tx_head - 1) & buff_mask)
    return
  wrapnum := buff_mask + 1 - tx_head
  num2 := 0
  if num1 > num
    num1 := num
  if num1 > wrapnum
    num2 := num1 - wrapnum
    num1 := wrapnum
  bytemove(@tx_buffer + tx_head, ptr, num1)
  bytemove(@tx_buffer, ptr + num1, num2)
  result := num1 + num2
  tx_head := (tx_head + result) & buff_mask

DAT

'***********************************
'* Assembly language serial driver *
'***********************************

                        org 0
'
'
' Entry
'
entry                   mov     t1,par                'get structure address
                        add     t1,#4 << 2            'skip past heads and tails

                        rdlong  t2,t1                 'get rx_pin
                        mov     rxmask,#1
                        shl     rxmask,t2

                        add     t1,#4                 'get tx_pin
                        rdlong  t2,t1
                        mov     txmask,#1
                        shl     txmask,t2

                        add     t1,#4                 'get rxtx_mode
                        rdlong  rxtxmode,t1

                        add     t1,#4                 'get bit_ticks
                        rdlong  bitticks,t1

                        add     t1,#4                 'get buffer_ptr
                        rdlong  rxbuff,t1
                        mov     txbuff,rxbuff
                        add     txbuff,#buff_size 'SRLM

                        test    rxtxmode,#%100  wz    'init tx pin according to mode
                        test    rxtxmode,#%010  wc
        if_z_ne_c       or      outa,txmask
        if_z            or      dira,txmask

                        mov     txcode,#transmit      'initialize ping-pong multitasking

'Speedup by PJV ======================================================================================
'insert this piece for one-time calculating pointer's hub addresses ===============================================

                        mov     HeadPtrAddr,par            
                        add     HeadPtrAddr,#2 << 2     'calc hubaddr of txhead index
                        mov     TailPtrAddr,HeadPtrAddr       '
                        add     TailPtrAddr,#4          'calc hubaddr of txtail index
                        

'======================================================================================================
'
' Receive
'
receive                 jmpret  rxcode,txcode         'run a chunk of transmit code, then return

                        test    rxtxmode,#%001  wz    'wait for start bit on rx pin
                        test    rxmask,ina      wc
        if_z_eq_c       jmp     #receive

                        mov     rxbits,#9             'ready to receive byte
                        mov     rxcnt,bitticks
                        shr     rxcnt,#1
                        add     rxcnt,cnt                          

:bit                    add     rxcnt,bitticks        'ready next bit period

:wait                   jmpret  rxcode,txcode         'run a chuck of transmit code, then return

                        mov     t1,rxcnt              'check if bit receive period done
                        sub     t1,cnt
                        cmps    t1,#0           wc
        if_nc           jmp     #:wait

                        test    rxmask,ina      wc    'receive bit on rx pin
                        rcr     rxdata,#1
                        djnz    rxbits,#:bit

                        shr     rxdata,#32-9          'justify and trim received byte
                        and     rxdata,#$FF
                        test    rxtxmode,#%001  wz    'if rx inverted, invert byte
        if_nz           xor     rxdata,#$FF

                        rdlong  t2,par                'save received byte and inc head
                        add     t2,rxbuff
                        wrbyte  rxdata,t2
                        sub     t2,rxbuff
                        add     t2,#1
                        and     t2,#buff_mask 'SRLM
                        wrlong  t2,par

                        jmp     #receive              'byte done, receive next byte
'
'
' Transmit
'
'Mod by PJV ==============================================================================================
'there are some redundant calculations here; to tighten it up, replaced this section ==================
{
transmit                jmpret  txcode,rxcode         'run a chunk of receive code, then return

                                                'check for head <> tail
                        mov     t1,par                'base object parameter address
                        add     t1,#2 << 2            'calc addr of txheadptr
                        rdlong  t2,t1                 'read txheadptr
                        add     t1,#1 << 2            'calc addr of txtailptr
                        rdlong  t3,t1                 'read txtailptr
                        cmp     t2,t3           wz    'compare
        if_z            jmp     #transmit             'jump if same

                                                'get byte and inc tail
                        add     t3,txbuff             'add txbuffer base to txtailptr to get current tail addr in txbuffer  
                        rdbyte  txdata,t3             'read txdata from txtail position in txbuffer
                        sub     t3,txbuff             'recalculate txtailptr
                        add     t3,#1                 'add one to point to next txbuffer location
                        and     t3,#$0F               'strip off overflow so LS nibble circulates
                        wrlong  t3,t1                 'writeback new txbuffer location to tailpointer in hub
}

'with this section ====================================================
                        rdlong  TxTailIndex,TailPtrAddr 'get tailindex only first time through
                        
transmit                jmpret  txcode,rxcode           'run a chunk of receive code, then return

                                                'check for headindex <> tailindex
                        rdlong  TxHeadIndex,HeadPtrAddr 'read tx head
                        cmp     TxHeadIndex,TxTailIndex wz 'compare indices...set z for match
        if_z            jmp     #transmit               'indirect jump to receiver if no new data

                                                'get byte and inc tail
                        add     TxTailIndex,txbuff    'add txbuffer base to txtailptr to get current tail addr in txbuffer  
                        rdbyte  txdata,TxTailIndex    'read txdata from txtail position in txbuffer
                        sub     TxTailIndex,txbuff    'recalculate txtailptr
                        add     TxTailIndex,#1        'add one to point to next txbuffer location
                        and     TxTailIndex,#buff_mask 'SRLM      'strip off overflow so LS nibble circulates
'optionally =================================================================================================
'for Spin only .... not required by assembler ====================================================================
                        wrlong  TxTailIndex,TailPtrAddr'optionally writeback new txbuffer location only if Spin requires it, else this line can be deleted
'================================================================================

                        or      txdata,#$100          'ready byte to transmit
                        shl     txdata,#2
                        or      txdata,#1
                        mov     txbits,#11
                        mov     txcnt,cnt

:bit                    test    rxtxmode,#%100  wz    'output bit on tx pin according to mode
                        test    rxtxmode,#%010  wc
        if_z_and_c      xor     txdata,#1
                        shr     txdata,#1       wc
        if_z            muxc    outa,txmask        
        if_nz           muxnc   dira,txmask
                        add     txcnt,bitticks        'ready next cnt

:wait                   jmpret  txcode,rxcode         'run a chunk of receive code, then return

                        mov     t1,txcnt              'check if bit transmit period done
                        sub     t1,cnt
                        cmps    t1,#0           wc
        if_nc           jmp     #:wait

                        djnz    txbits,#:bit          'another bit to transmit?

                        jmp     #transmit             'byte done, transmit next byte
'
'
' Uninitialized data
'
' insert these reserves ================================================================================
HeadPtrAddr             res     1
TailPtrAddr             res     1
TxHeadIndex             res     1
TxTailIndex             res     1
'=======================================================================================================

t1                      res     1
t2                      res     1
t3                      res     1

rxtxmode                res     1
bitticks                res     1

rxmask                  res     1
rxbuff                  res     1
rxdata                  res     1
rxbits                  res     1
rxcnt                   res     1
rxcode                  res     1

txmask                  res     1
txbuff                  res     1
txdata                  res     1
txbits                  res     1
txcnt                   res     1
txcode                  res     1

{{

┌──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                                   TERMS OF USE: MIT License                                                  │                                                            
├──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation    │ 
│files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy,    │
│modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software│
│is furnished to do so, subject to the following conditions:                                                                   │
│                                                                                                                              │
│The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.│
│                                                                                                                              │
│THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE          │
│WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR         │
│COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,   │
│ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.                         │
└──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘
}}
