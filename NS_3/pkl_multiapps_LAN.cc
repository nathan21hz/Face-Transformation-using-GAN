/* -*- Mode:C++; c-file-style:"gnu"; indent-tabs-mode:nil; -*- */
/*
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License version 2 as
 * published by the Free Software Foundation;
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program; if not, write to the Free Software
 * Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
 */

#include <fstream>
#include <iostream>
#include <string>
#include "ns3/core-module.h"
#include "ns3/network-module.h"
#include "ns3/csma-module.h"
#include "ns3/internet-module.h"
#include "ns3/point-to-point-module.h"
#include "ns3/applications-module.h"
#include "ns3/ipv4-global-routing-helper.h"
#include "ns3/stats-module.h"


// Default Network Topology
//
//                      10.1.1.0
// n2   n3   n4   n0 -------------- n1   n5   n6   n7
//  |    |    |    | point-to-point  |    |    |    |
//  ================                 ================
//    LAN 10.1.2.0                     LAN 10.1.3.0

using namespace ns3;

NS_LOG_COMPONENT_DEFINE("pkl_myApp_LAN");

void WriteUntilBufferFull(Ptr<Socket>, uint32_t);

class MyApp : public Application
{

public:
    MyApp();
    virtual ~MyApp();

    /**
   * Register this type.
   * \return The TypeId.
   */
    static TypeId GetTypeId(void);
    void Setup(Ptr<Socket> socket, Address address, uint32_t packetSize, uint32_t nPackets, DataRate dataRate,std::string filename);

private:
    virtual void StartApplication(void);
    virtual void StopApplication(void);

    void ScheduleTx(void);
    void SendPacket(void);

    void WriteUntilBufferFull(Ptr<Socket> , uint32_t);

    Ptr<Socket> m_socket;
    Address m_peer;
    uint32_t m_packetSize;
    uint32_t m_nPackets;
    DataRate m_dataRate;
    EventId m_sendEvent;
    bool m_running;
    uint32_t m_packetsSent;
    uint32_t m_totalTxBytes;
    uint32_t m_currentTxBytes;
    const uint8_t *m_data;
    std::string m_filename;
};

MyApp::MyApp()
    : m_socket(0),
      m_peer(),
      m_packetSize(0),
      m_nPackets(0),
      m_dataRate(0),
      m_sendEvent(),
      m_running(false),
      m_packetsSent(0),
      m_totalTxBytes(0),
      m_currentTxBytes(0)
{

}

MyApp::~MyApp()
{
    m_socket = 0;
}

/* static */
TypeId MyApp::GetTypeId(void)
{
    static TypeId tid = TypeId("MyApp")
                            .SetParent<Application>()
                            .SetGroupName("Tutorial")
                            .AddConstructor<MyApp>();
    return tid;
}

void MyApp::Setup(Ptr<Socket> socket, Address address, uint32_t packetSize, uint32_t nPackets, DataRate dataRate, std::string filename)
{
    m_socket = socket;
    m_peer = address;
    m_packetSize = packetSize;
    m_nPackets = nPackets;
    m_dataRate = dataRate;
    m_filename=filename;
}

void MyApp::StartApplication(void)
{
    m_running = true;
    m_packetsSent = 0;
    if (InetSocketAddress::IsMatchingType(m_peer))
    {
        m_socket->Bind();
    }
    else
    {
        m_socket->Bind6();
    }
    m_socket->Connect(m_peer);
    SendPacket();
}

void MyApp::StopApplication(void)
{
    m_running = false;

    if (m_sendEvent.IsRunning())
    {
        Simulator::Cancel(m_sendEvent);
    }

    if (m_socket)
    {
        m_socket->Close();
    }
}



void MyApp::SendPacket(void)
{
    m_socket->SetSendCallback(MakeCallback(&MyApp::WriteUntilBufferFull,this));

    // std::basic_string::char_type *buffer;
    std::ifstream inFile(m_filename, std::ios::in | std::ios::binary); //二进制读方式打开
    if (!inFile.is_open())
    {
        exit(1);
    }
    uint32_t begin = inFile.tellg();
    // printf("%d\n", begin);
    inFile.seekg(0, std::ios::end);
    uint32_t end = inFile.tellg();
    // printf("%d\n", end);
    m_totalTxBytes = end - begin;
    char buffer[m_totalTxBytes];
    inFile.seekg(0, std::ios::beg);
    inFile.read(buffer, m_totalTxBytes);
    inFile.close();

    m_data = (const uint8_t *)buffer;
    // m_currentTxBytes = 0;
    static const uint32_t writeSize = m_packetSize;

    WriteUntilBufferFull(m_socket, writeSize);
}

void MyApp::WriteUntilBufferFull(Ptr<Socket> localSocket, uint32_t spaceAvailable)
{   
    printf("%d\n", spaceAvailable);
    uint32_t left = m_totalTxBytes - m_currentTxBytes;
    printf("%d\n", left);
    printf("%d\n", m_packetsSent);
    while (m_currentTxBytes < m_totalTxBytes && m_packetsSent < m_nPackets && m_socket->GetTxAvailable()>0)
    {
        left = m_totalTxBytes - m_currentTxBytes;
        uint32_t toWrite = std::min(m_packetSize, left);
        toWrite = std::min(toWrite, m_socket->GetTxAvailable());

        Ptr<Packet> packet = Create<Packet>(&m_data[m_currentTxBytes], toWrite);
        uint32_t amountSent = m_socket->Send(packet);

        if (amountSent < 0)
        {
            // we will be called again when new tx space becomes available.
            return;
        }
        printf("%d\n", amountSent);

        m_currentTxBytes += amountSent;
        m_packetsSent++;
    }

    printf("%d\n", m_currentTxBytes);

    if (m_currentTxBytes >= m_totalTxBytes)
    {
        m_socket->Close();
    }
}

void MyApp::ScheduleTx(void)
{
    if (m_running)
    {
        Time tNext(Seconds(m_packetSize * 8 / static_cast<double>(m_dataRate.GetBitRate())));
        m_sendEvent = Simulator::Schedule(tNext, &MyApp::SendPacket, this);
    }
}

static void
CwndChange(Ptr<OutputStreamWrapper> stream, uint32_t oldCwnd, uint32_t newCwnd)
{
    NS_LOG_UNCOND(Simulator::Now().GetSeconds() << "\t" << newCwnd);
    *stream->GetStream() << Simulator::Now().GetSeconds() << "\t" << oldCwnd << "\t" << newCwnd << std::endl;
}

static void
RxDrop(Ptr<PcapFileWrapper> file, Ptr<const Packet> p)
{
    NS_LOG_UNCOND("RxDrop at " << Simulator::Now().GetSeconds());
    file->Write(Simulator::Now(), p);
}


int main(int argc, char *argv[])
{
    bool verbose = true;
    uint32_t nCsma1 = 3;
    uint32_t nCsma2 = 3;

    CommandLine cmd(__FILE__);
    cmd.AddValue("nCsma1", "Number of \"extra\" CSMA1 nodes/devices", nCsma1);
    cmd.AddValue("nCsma2", "Number of \"extra\" CSMA2 nodes/devices", nCsma2);
    cmd.AddValue("verbose", "Tell echo applications to log if true", verbose);

    cmd.Parse(argc, argv);

    if (verbose)
    {
        LogComponentEnable("pkl_myApp_LAN", LOG_LEVEL_ERROR);
    }

    nCsma1 = nCsma1 == 0 ? 1 : nCsma1;
    nCsma2 = nCsma2 == 0 ? 1 : nCsma2;

    NodeContainer p2pNodes;
    p2pNodes.Create(2);

    NodeContainer csmaNodes1;
    csmaNodes1.Add(p2pNodes.Get(0));
    csmaNodes1.Create(nCsma1);

    NodeContainer csmaNodes2;
    csmaNodes2.Add(p2pNodes.Get(1));
    csmaNodes2.Create(nCsma2);

    PointToPointHelper pointToPoint;
    pointToPoint.SetDeviceAttribute("DataRate", StringValue("5Mbps"));
    pointToPoint.SetChannelAttribute("Delay", StringValue("2ms"));

    NetDeviceContainer p2pDevices;
    p2pDevices = pointToPoint.Install(p2pNodes);

    CsmaHelper csma;
    csma.SetChannelAttribute("DataRate", StringValue("100Mbps"));
    csma.SetChannelAttribute("Delay", TimeValue(NanoSeconds(6560)));

    NetDeviceContainer csmaDevices1;
    csmaDevices1 = csma.Install(csmaNodes1);

    NetDeviceContainer csmaDevices2;
    csmaDevices2 = csma.Install(csmaNodes2);

    Ptr<RateErrorModel> em = CreateObject<RateErrorModel>();
    em->SetAttribute("ErrorRate", DoubleValue(0.00001));
    csmaDevices2.Get(nCsma2)->SetAttribute("ReceiveErrorModel", PointerValue(em));
    csmaDevices2.Get(0)->SetAttribute("ReceiveErrorModel", PointerValue(em));

    InternetStackHelper stack;
    stack.Install(csmaNodes1);
    stack.Install(csmaNodes2);

    uint16_t sinkPort = 8080;
    Address sinkAddress_n7;
    Address anyAddress;
    Address sinkAddress_n1;
    std::string probeType;
    std::string tracePath;

    Ipv4AddressHelper address;
    address.SetBase("10.1.1.0", "255.255.255.0");
    Ipv4InterfaceContainer p2pInterfaces;
    p2pInterfaces = address.Assign(p2pDevices);

    address.SetBase("10.1.2.0", "255.255.255.0");
    Ipv4InterfaceContainer csmaInterfaces1;
    csmaInterfaces1 = address.Assign(csmaDevices1);

    address.SetBase("10.1.3.0", "255.255.255.0");
    Ipv4InterfaceContainer csmaInterfaces2;
    csmaInterfaces2 = address.Assign(csmaDevices2);
    sinkAddress_n7 = InetSocketAddress(csmaInterfaces2.GetAddress(nCsma2), sinkPort);

    sinkAddress_n1 = InetSocketAddress(csmaInterfaces2.GetAddress(0), sinkPort);
    anyAddress = InetSocketAddress(Ipv4Address::GetAny(), sinkPort);
    probeType = "ns3::Ipv4PacketProbe";
    tracePath = "/NodeList/*/$ns3::Ipv4L3Protocol/Tx";

    PacketSinkHelper packetSinkHelper("ns3::TcpSocketFactory", anyAddress);
    ApplicationContainer sinkApps_n7 = packetSinkHelper.Install(csmaNodes2.Get(nCsma2));
    ApplicationContainer sinkApps_n1 = packetSinkHelper.Install(csmaNodes2.Get(0));


    sinkApps_n7.Start(Seconds(0.));
    sinkApps_n7.Stop(Seconds(20.));
    
    sinkApps_n1.Start(Seconds(0.));
    sinkApps_n1.Stop(Seconds(20.));

    Ptr<Socket> ns3TcpSocket_n4 = Socket::CreateSocket(csmaNodes1.Get(nCsma1), TcpSocketFactory::GetTypeId());
    Ptr<Socket> ns3TcpSocket_n2 = Socket::CreateSocket(csmaNodes1.Get(1), TcpSocketFactory::GetTypeId());

    Ptr<MyApp> app_n4 = CreateObject<MyApp>();
    app_n4->Setup(ns3TcpSocket_n4, sinkAddress_n7, 1072, 10000000, DataRate("1Mbps"), "data_pkl/kp_driving_Obama.pkl");
    csmaNodes1.Get(nCsma1)->AddApplication(app_n4);
    app_n4->SetStartTime(Seconds(1.));
    app_n4->SetStopTime(Seconds(20.));

    Ptr<MyApp> app_n2 = CreateObject<MyApp>();
    app_n2->Setup(ns3TcpSocket_n2, sinkAddress_n1, 1072, 10000000, DataRate("1Mbps"), "data_pkl/LeslieCheung.mp4");
    csmaNodes1.Get(1)->AddApplication(app_n2);
    app_n2->SetStartTime(Seconds(1.));
    app_n2->SetStopTime(Seconds(20.));

    Ipv4GlobalRoutingHelper::PopulateRoutingTables(); 

    AsciiTraceHelper asciiTraceHelper;
    Ptr<OutputStreamWrapper> stream = asciiTraceHelper.CreateFileStream("pkl_multiapps_LAN.cwnd");
    ns3TcpSocket_n4->TraceConnectWithoutContext("CongestionWindow", MakeBoundCallback(&CwndChange, stream));
    ns3TcpSocket_n2->TraceConnectWithoutContext("CongestionWindow", MakeBoundCallback(&CwndChange, stream));


    pointToPoint.EnablePcapAll("pkl_multiapps_LAN");
    csma.EnablePcap("pkl_multiapps_LAN", csmaDevices2.Get(nCsma2), true);
    csma.EnablePcap("pkl_multiapps_LAN", csmaDevices1.Get(nCsma1), true);
    csma.EnablePcap("pkl_multiapps_LAN", csmaDevices2.Get(0), true);
    csma.EnablePcap("pkl_multiapps_LAN", csmaDevices1.Get(1), true);

    PcapHelper pcapHelper;
    Ptr<PcapFileWrapper> file = pcapHelper.CreateFile("pkl_multiapps_LAN_RxDrop.pcap", std::ios::out, PcapHelper::DLT_PPP);
    csmaDevices2.Get(nCsma2)->TraceConnectWithoutContext("PhyRxDrop", MakeBoundCallback(&RxDrop, file));
    csmaDevices2.Get(0)->TraceConnectWithoutContext("PhyRxDrop", MakeBoundCallback(&RxDrop, file));

    // Use GnuplotHelper to plot the packet byte count over time
    GnuplotHelper plotHelper;

    // Configure the plot.  The first argument is the file name prefix
    // for the output files generated.  The second, third, and fourth
    // arguments are, respectively, the plot title, x-axis, and y-axis labels
    plotHelper.ConfigurePlot("pkl_multiapps_LAN-packet-byte-count",
                             "Packet Byte Count vs. Time",
                             "Time (Seconds)",
                             "Packet Byte Count");

    // Specify the probe type, trace source path (in configuration namespace), and
    // probe output trace source ("OutputBytes") to plot.  The fourth argument
    // specifies the name of the data series label on the plot.  The last
    // argument formats the plot by specifying where the key should be placed.
    plotHelper.PlotProbe(probeType,
                         tracePath,
                         "OutputBytes",
                         "Packet Byte Count",
                         GnuplotAggregator::KEY_BELOW);

    // Use FileHelper to write out the packet byte count over time
    FileHelper fileHelper;

    // Configure the file to be written, and the formatting of output data.
    fileHelper.ConfigureFile("pkl_multiapps_LAN-packet-byte-count",
                             FileAggregator::FORMATTED);

    // Set the labels for this formatted output file.
    fileHelper.Set2dFormat("Time (Seconds) = %.3e\tPacket Byte Count = %.0f");

    // Specify the probe type, trace source path (in configuration namespace), and
    // probe output trace source ("OutputBytes") to write.
    fileHelper.WriteProbe(probeType,
                          tracePath,
                          "OutputBytes");

    Simulator::Stop(Seconds(20));
    Simulator::Run();
    Simulator::Destroy();

    return 0;
}