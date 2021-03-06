
2.4GHz 802.11b/g/n/ax channel description
802.11b: DSSS, 22MHZ channel width, 
802.11g: OFDM, 20MHz channel width (tighter)
802.11n: OFDM, 20/40MHz channel width 

| channel | center | range (B) | range (G)| range (N)
|---------|--------|-----------|-----------|-------------|
| 1       | 2412   | 2401–2423 | 2402-2422 |             |
| 2       | 2417   | 2406–2428 | 2407-2427 |             |
| 3       | 2422   | 2411–2433 | 2412-2432 | 2402 - 2442 |
| 4       | 2427   | 2416–2438 | 2417-2437 |             |
| 5       | 2432   | 2421–2443 | 2422-2442 |             |
| 6       | 2437   | 2426–2448 | 2427-2447 |             |
| 7       | 2442   | 2431–2453 | 2432-2452 |             |
| 8       | 2447   | 2436–2458 | 2437-2457 |             |
| 9       | 2452   | 2441–2463 | 2442-2462 |             |
| 10      | 2457   | 2446–2468 | 2447-2467 |             |
| 11      | 2462   | 2451–2473 | 2452-2472 | 2442 - 2482 |
| 12*     | 2467   | 2456–2478 | 2457-2477 |             |
| 13*     | 2472   | 2461–2483 | 2462-2482 |             |
| 14*     | 2484   | 2473–2495 | 2474-2494 |             |

40 Mhz 2.4Ghz channel notation:
only two non-overlappy 40Mhz wide bands. 
40Mhz channel notation:
|   range   |  a  |  b   | c  | d  |  e     | f        |
|-----------|-----|------|----|----|--------|----------|
| 2402-2482 | Ch3 | 1+5  | 1+ | 5- | 1+Upper| 5+Lower  |
| 2442-2482 | Ch11| 9+13 | 9+ | 13-| 9+Upper| 13+Lower |


1999  (802.11a) Orthogonal Frequency Division Multiplexing (ODFM) technology brought data rates of 6 - 54 Mbps to 5 GHz

1999 (802.11b) HR-DSSS) mechanisms that brought higher data rates of 5.5 and 11 Mbps to the more commonly used 2.4 GHz

2003 (802.11g)  brought OFDM technology and the data rates of 6 - 54 Mbps to the 2.4 GHz frequency band

2009 (802.11n) amendment which defines the use of High Throughput (HT) radios which have the potential to support data rates as high as 600 Mbps. 802.11n technology uses both PHY and MAC layer enhancements to achieve these high data rates.


MIMO - (Spatial Multiplexing) transmit multiple unique streams of data on the same frequency which increases throughput. MIMO transmitters and receivers use multiple radios and antennas, called radio chains. 

Radio chains - Any single radio along with all of its supporting architecture such as mixers, amplifiers, and analog/digital converters can be defined as a radio chain. MIMO systems use multiple radio chains, with each radio chain having its own antenna. Each MIMO system is defined by the number of transmitters and receivers used by the multiple radio chains. The 802.11n-2009 amendment allows for MIMO 4×4 systems using up to four radio chains. In a MIMO system, the first number always references the transmitters (TX), and the second number references the receivers (RX).

For example, a 3×4 MIMO system would consist of four radio chains with three transmitters and four receivers.A 4×4 MIMO system would use four radio chains with four transmitters and four receivers. Each radio chain requires power. A 4×4 MIMO system would require much more of a power draw than a 2×2 MIMO system.

Currently, most enterprise WLAN vendors are using 2x3 or 3x3 MIMO radio systems. A dual-frequency access point requires two separate 2x3 MIMO systems for both the 2.4 GHz and 5 GHz frequency bands.


  TxR:S
Transmit Antennas x Receive Antennas : Spatial Streams
  T – Transmit Antennas
  R – Receive Antennas
  S – Spatial Streams (1 = 150Mbps, 2 = 300Mbps)
  The 1250 and 1140 are 2x3:2
Two Transmit, Three Receive, Two Spatial Streams
  NOTE: Beware the taxonomy... vendors claiming 3x3 and 4x4 MIMO systems still only do 2 spatial streams!


Idea: Is the 'correct' way to determine TxR:S info by working backwards from maximum supported MCS?

Both tag 45 (HT capabilities) and 61 (HT Information) contains fields that wireshark labels "MCS

45 (Capabilites)
Rx Supported Modulation and Coding Scheme Set: MCS Set
61 (Info)
Rx Supported Modulation and Coding Scheme Set: Basic MCS Set

Basic MCS Set:  You have to be this tall to ride? (minimal SpatialStreams)
   Often seen as 0x0000000000000.. Does 0 Max TX SS's imply HT support not required?

   An MCS is identified by an MCS index, which is represented by an integer in the range 0 to 76. The interpretation of the MCS index (i.e., the mapping from MCS to data rate) is PHY dependent. For the HT PHY, see 19.5.

maxlen(MCSSET == 76?) (1 per MCS specified?)