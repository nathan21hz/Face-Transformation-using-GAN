set terminal png
set output "pkl_multiapps_LAN-packet-byte-count.png"
set title "Packet Byte Count vs. Time \n\nTrace Source Path: /NodeList/*/$ns3::Ipv4L3Protocol/Tx"
set xlabel "Time (Seconds)"
set ylabel "Packet Byte Count"

set key outside center below
set datafile missing "-nan"
plot "pkl_multiapps_LAN-packet-byte-count.dat" index 0 title "Packet Byte Count-0" with linespoints, "pkl_multiapps_LAN-packet-byte-count.dat" index 1 title "Packet Byte Count-1" with linespoints, "pkl_multiapps_LAN-packet-byte-count.dat" index 2 title "Packet Byte Count-2" with linespoints, "pkl_multiapps_LAN-packet-byte-count.dat" index 3 title "Packet Byte Count-4" with linespoints, "pkl_multiapps_LAN-packet-byte-count.dat" index 4 title "Packet Byte Count-7" with linespoints
