from lnst.Controller.Task import ctl
from lnst.Controller.PerfRepoUtils import netperf_baseline_template
from lnst.Controller.PerfRepoUtils import netperf_result_template

from lnst.RecipeCommon.IRQ import pin_dev_irqs
from lnst.RecipeCommon.PerfRepo import generate_perfrepo_comment
from lnst.RecipeCommon.Offloads import parse_offloads

# ------
# SETUP
# ------

mapping_file = ctl.get_alias("mapping_file")
perf_api = ctl.connect_PerfRepo(mapping_file)

product_name = ctl.get_alias("product_name")

m1 = ctl.get_host("testmachine1")
m2 = ctl.get_host("testmachine2")

m1.sync_resources(modules=["IcmpPing", "Icmp6Ping", "Netperf"])
m2.sync_resources(modules=["IcmpPing", "Icmp6Ping", "Netperf"])

# ------
# TESTS
# ------

vlans = ["vlan10", "vlan20", "vlan30"]

ipv = ctl.get_alias("ipv")
mtu = ctl.get_alias("mtu")
netperf_duration = int(ctl.get_alias("netperf_duration"))
nperf_reserve = int(ctl.get_alias("nperf_reserve"))
nperf_confidence = ctl.get_alias("nperf_confidence")
nperf_max_runs = int(ctl.get_alias("nperf_max_runs"))
nperf_cpupin = ctl.get_alias("nperf_cpupin")
nperf_cpu_util = ctl.get_alias("nperf_cpu_util")
nperf_mode = ctl.get_alias("nperf_mode")
nperf_num_parallel = int(ctl.get_alias("nperf_num_parallel"))
nperf_debug = ctl.get_alias("nperf_debug")
nperf_max_dev = ctl.get_alias("nperf_max_dev")
nperf_msg_size = ctl.get_alias("nperf_msg_size")
pr_user_comment = ctl.get_alias("perfrepo_comment")
offloads_alias = ctl.get_alias("offloads")
nperf_protocols = ctl.get_alias("nperf_protocols")

sctp_default_msg_size = "16K"

if offloads_alias is not None:
    offloads, offload_settings = parse_offloads(offloads_alias)
else:
    offloads = ["gro", "gso", "tso", "tx"]
    offload_settings = [ [("gro", "on"), ("gso", "on"), ("tso", "on"), ("tx", "on")],
                         [("gro", "off"), ("gso", "on"), ("tso", "on"), ("tx", "on")],
                         [("gro", "on"), ("gso", "off"),  ("tso", "off"), ("tx", "on")],
                         [("gro", "on"), ("gso", "on"), ("tso", "off"), ("tx", "off")]]

pr_comment = generate_perfrepo_comment([m1, m2], pr_user_comment)

m1_bond = m1.get_interface("test_bond")
m1_bond.set_mtu(mtu)
m1_phy1 = m1.get_interface("eth1")
m1_phy2 = m1.get_interface("eth2")
m2_phy1 = m2.get_interface("eth1")
m2_phy1.set_mtu(mtu)

for vlan in vlans:
    vlan_if1 = m1.get_interface(vlan)
    vlan_if1.set_mtu(mtu)
    vlan_if2 = m2.get_interface(vlan)
    vlan_if2.set_mtu(mtu)

if nperf_cpupin:
    # this will pin devices irqs to cpu #0
    m1.run("service irqbalance stop")
    m2.run("service irqbalance stop")

    for m, d in [ (m1, m1_phy1), (m1, m1_phy2), (m2, m2_phy1) ]:
        pin_dev_irqs(m, d, 0)

ctl.wait(15)

ping_mod = ctl.get_module("IcmpPing",
                           options={
                               "count" : 100,
                               "interval" : 0.1
                           })
ping_mod6 = ctl.get_module("Icmp6Ping",
                           options={
                               "count" : 100,
                               "interval" : 0.1
                           })

m1_vlan1 = m1.get_interface(vlans[0])
m2_vlan1 = m2.get_interface(vlans[0])

p_opts = "-L %s" % (m2_vlan1.get_ip(0))
if nperf_cpupin and nperf_mode != "multi":
    p_opts += " -T%s,%s" % (nperf_cpupin, nperf_cpupin)

p_opts6 = "-L %s -6" % (m2_vlan1.get_ip(1))
if nperf_cpupin and nperf_mode != "multi":
    p_opts6 += " -T%s,%s" % (nperf_cpupin, nperf_cpupin)

netperf_srv = ctl.get_module("Netperf",
                              options={
                                  "role" : "server",
                                  "bind": m1_vlan1.get_ip(0)
                              })
netperf_srv6 = ctl.get_module("Netperf",
                              options={
                                  "role" : "server",
                                  "bind": m1_vlan1.get_ip(1),
                                  "netperf_opts" : " -6"
                              })
netperf_cli_tcp = ctl.get_module("Netperf",
                                  options={
                                      "role" : "client",
                                      "netperf_server": m1_vlan1.get_ip(0),
                                      "duration" : netperf_duration,
                                      "testname" : "TCP_STREAM",
                                      "confidence" : nperf_confidence,
                                      "cpu_util" : nperf_cpu_util,
                                      "runs": nperf_max_runs,
                                      "netperf_opts": p_opts,
                                      "debug" : nperf_debug,
                                      "max_deviation" : nperf_max_dev
                                  })
netperf_cli_udp = ctl.get_module("Netperf",
                                  options={
                                      "role" : "client",
                                      "netperf_server": m1_vlan1.get_ip(0),
                                      "duration" : netperf_duration,
                                      "testname" : "UDP_STREAM",
                                      "confidence" : nperf_confidence,
                                      "cpu_util" : nperf_cpu_util,
                                      "runs": nperf_max_runs,
                                      "netperf_opts": p_opts,
                                      "debug" : nperf_debug,
                                      "max_deviation" : nperf_max_dev
                                  })
netperf_cli_tcp6 = ctl.get_module("Netperf",
                                  options={
                                      "role" : "client",
                                      "netperf_server": m1_vlan1.get_ip(1),
                                      "duration" : netperf_duration,
                                      "testname" : "TCP_STREAM",
                                      "confidence" : nperf_confidence,
                                      "cpu_util" : nperf_cpu_util,
                                      "runs": nperf_max_runs,
                                      "netperf_opts": p_opts6,
                                      "debug" : nperf_debug,
                                      "max_deviation" : nperf_max_dev
                                  })
netperf_cli_udp6 = ctl.get_module("Netperf",
                                  options={
                                      "role" : "client",
                                      "netperf_server": m1_vlan1.get_ip(1),
                                      "duration" : netperf_duration,
                                      "testname" : "UDP_STREAM",
                                      "confidence" : nperf_confidence,
                                      "cpu_util" : nperf_cpu_util,
                                      "runs": nperf_max_runs,
                                      "netperf_opts": p_opts6,
                                      "debug" : nperf_debug,
                                      "max_deviation" : nperf_max_dev
                                  })

netperf_cli_sctp = ctl.get_module("Netperf",
                                  options={
                                      "role" : "client",
                                      "netperf_server" : m1_vlan1.get_ip(0),
                                      "duration" : netperf_duration,
                                      "testname" : "SCTP_STREAM",
                                      "confidence" : nperf_confidence,
                                      "cpu_util" : nperf_cpu_util,
                                      "runs" : nperf_max_runs,
                                      "netperf_opts" : p_opts,
                                      "msg_size" : sctp_default_msg_size,
                                      "debug" : nperf_debug,
                                      "max_deviation" : nperf_max_dev
                                  })

netperf_cli_sctp6 = ctl.get_module("Netperf",
                                  options={
                                      "role" : "client",
                                      "netperf_server" : m1_vlan1.get_ip(1),
                                      "duration" : netperf_duration,
                                      "testname" : "SCTP_STREAM",
                                      "confidence" : nperf_confidence,
                                      "cpu_util" : nperf_cpu_util,
                                      "runs" : nperf_max_runs,
                                      "netperf_opts" : p_opts6,
                                      "msg_size" : sctp_default_msg_size,
                                      "debug" : nperf_debug,
                                      "max_deviation" : nperf_max_dev
                                  })

if nperf_mode == "multi":
    netperf_cli_tcp.unset_option("confidence")
    netperf_cli_udp.unset_option("confidence")
    netperf_cli_sctp.unset_option("confidence")
    netperf_cli_tcp6.unset_option("confidence")
    netperf_cli_udp6.unset_option("confidence")
    netperf_cli_sctp6.unset_option("confidence")

    netperf_cli_tcp.update_options({"num_parallel": nperf_num_parallel})
    netperf_cli_udp.update_options({"num_parallel": nperf_num_parallel})
    netperf_cli_sctp.update_options({"num_parallel": nperf_num_parallel})
    netperf_cli_tcp6.update_options({"num_parallel": nperf_num_parallel})
    netperf_cli_udp6.update_options({"num_parallel": nperf_num_parallel})
    netperf_cli_sctp6.update_options({"num_parallel": nperf_num_parallel})

    # we have to use multiqueue qdisc to get appropriate data
    m1.run("tc qdisc replace dev %s root mq" % m1_phy1.get_devname())
    m1.run("tc qdisc replace dev %s root mq" % m1_phy2.get_devname())
    m2.run("tc qdisc replace dev %s root mq" % m2_phy1.get_devname())

if nperf_msg_size is not None:
    netperf_cli_tcp.update_options({"msg_size" : nperf_msg_size})
    netperf_cli_udp.update_options({"msg_size" : nperf_msg_size})
    netperf_cli_sctp.update_options({"msg_size" : nperf_msg_size})
    netperf_cli_tcp6.update_options({"msg_size" : nperf_msg_size})
    netperf_cli_udp6.update_options({"msg_size" : nperf_msg_size})
    netperf_cli_sctp6.update_options({"msg_size" : nperf_msg_size})

for setting in offload_settings:
    #apply offload setting
    dev_features = ""
    for offload in setting:
        dev_features += " %s %s" % (offload[0], offload[1])

    m1.run("ethtool -K %s %s" % (m1_phy1.get_devname(),
                                 dev_features))
    m1.run("ethtool -K %s %s" % (m1_phy2.get_devname(),
                                 dev_features))
    m2.run("ethtool -K %s %s" % (m2_phy1.get_devname(),
                                 dev_features))

    # Ping test
    for vlan1 in vlans:
        m1_vlan1 = m1.get_interface(vlan1)
        for vlan2 in vlans:
            m2_vlan2 = m2.get_interface(vlan2)

            ping_mod.update_options({"addr": m2_vlan2.get_ip(0),
                                     "iface": m1_vlan1.get_devname()})

            ping_mod6.update_options({"addr": m2_vlan2.get_ip(1),
                                      "iface": m1_vlan1.get_ip(1)})

            if vlan1 == vlan2:
                # These tests should pass
                # Ping between same VLANs
                if ipv in [ 'ipv4', 'both' ]:
                    m1.run(ping_mod)

                if ipv in [ 'ipv6', 'both' ]:
                    m1.run(ping_mod6)
            else:
                # These tests should fail
                # Ping across different VLAN
                if ipv in [ 'ipv4', 'both' ]:
                    m1.run(ping_mod, expect="fail")

    # Netperf test (both TCP and UDP)
    if ipv in [ 'ipv4', 'both' ]:
        srv_proc = m1.run(netperf_srv, bg=True)
        ctl.wait(2)

        if nperf_protocols.find("tcp") > -1:
            # prepare PerfRepo result for tcp
            result_tcp = perf_api.new_result("tcp_ipv4_id",
                                             "tcp_ipv4_result",
                                             hash_ignore=[
                                                 'kernel_release',
                                                 'redhat_release'])
            for offload in setting:
                result_tcp.set_parameter(offload[0], offload[1])

            if nperf_msg_size is not None:
                result_tcp.set_parameter("nperf_msg_size", nperf_msg_size)

            result_tcp.set_parameter('netperf_server_on_vlan', vlans[0])
            result_tcp.set_parameter('netperf_client_on_vlan', vlans[0])
            result_tcp.add_tag(product_name)
            if nperf_mode == "multi":
                result_tcp.add_tag("multithreaded")
                result_tcp.set_parameter('num_parallel', nperf_num_parallel)

            baseline = perf_api.get_baseline_of_result(result_tcp)
            netperf_baseline_template(netperf_cli_tcp, baseline)

            tcp_res_data = m2.run(netperf_cli_tcp,
                                  timeout = (netperf_duration + nperf_reserve)*nperf_max_runs)

            netperf_result_template(result_tcp, tcp_res_data)
            result_tcp.set_comment(pr_comment)
            perf_api.save_result(result_tcp)

        if nperf_protocols.find("udp") > -1 and ("gro", "off") not in setting:
            # prepare PerfRepo result for udp
            result_udp = perf_api.new_result("udp_ipv4_id",
                                             "udp_ipv4_result",
                                             hash_ignore=[
                                                 'kernel_release',
                                                 'redhat_release'])
            for offload in setting:
                result_udp.set_parameter(offload[0], offload[1])

            if nperf_msg_size is not None:
                result_udp.set_parameter("nperf_msg_size", nperf_msg_size)

            result_udp.set_parameter('netperf_server_on_vlan', vlans[0])
            result_udp.set_parameter('netperf_client_on_vlan', vlans[0])
            result_udp.add_tag(product_name)
            if nperf_mode == "multi":
                result_udp.add_tag("multithreaded")
                result_udp.set_parameter('num_parallel', nperf_num_parallel)

            baseline = perf_api.get_baseline_of_result(result_udp)
            netperf_baseline_template(netperf_cli_udp, baseline)

            udp_res_data = m2.run(netperf_cli_udp,
                                  timeout = (netperf_duration + nperf_reserve)*nperf_max_runs)

            netperf_result_template(result_udp, udp_res_data)
            result_udp.set_comment(pr_comment)
            perf_api.save_result(result_udp)

        # for SCTP only gso offload on/off
        if (nperf_protocols.find("sctp") > -1 and
              (len([val for val in setting if val[1] == 'off']) == 0 or
               ('gso', 'off') in setting)):
            result_sctp = perf_api.new_result("sctp_ipv4_id",
                                              "sctp_ipv4_result",
                                              hash_ignore=[
                                                  'kernel_release',
                                                  'redhat_release'])
            for offload in setting:
                result_sctp.set_parameter(offload[0], offload[1])

            result_sctp.set_parameter('netperf_server_on_vlan', vlans[0])
            result_sctp.set_parameter('netperf_client_on_vlan', vlans[0])
            result_sctp.add_tag(product_name)
            if nperf_mode == "multi":
                result_sctp.add_tag("multithreaded")
                result_sctp.set_parameter("num_parallel", nperf_num_parallel)

            baseline = perf_api.get_baseline_of_result(result_sctp)
            netperf_baseline_template(netperf_cli_sctp, baseline)
            sctp_res_data = m2.run(netperf_cli_sctp,
                                   timeout = (netperf_duration + nperf_reserve)*nperf_max_runs)

            netperf_result_template(result_sctp, sctp_res_data)
            result_sctp.set_comment(pr_comment)
            perf_api.save_result(result_sctp)

        srv_proc.intr()

    if ipv in [ 'ipv6', 'both' ]:
        srv_proc = m1.run(netperf_srv6, bg=True)
        ctl.wait(2)

        if nperf_protocols.find("tcp") > -1:
            # prepare PerfRepo result for tcp ipv6
            result_tcp = perf_api.new_result("tcp_ipv6_id",
                                             "tcp_ipv6_result",
                                             hash_ignore=[
                                                 'kernel_release',
                                                 'redhat_release'])
            for offload in setting:
                result_tcp.set_parameter(offload[0], offload[1])

            if nperf_msg_size is not None:
                result_tcp.set_parameter("nperf_msg_size", nperf_msg_size)

            result_tcp.set_parameter('netperf_server_on_vlan', vlans[0])
            result_tcp.set_parameter('netperf_client_on_vlan', vlans[0])
            result_tcp.add_tag(product_name)
            if nperf_mode == "multi":
                result_tcp.add_tag("multithreaded")
                result_tcp.set_parameter('num_parallel', nperf_num_parallel)

            baseline = perf_api.get_baseline_of_result(result_tcp)
            netperf_baseline_template(netperf_cli_tcp6, baseline)

            tcp_res_data = m2.run(netperf_cli_tcp6,
                                  timeout = (netperf_duration + nperf_reserve)*nperf_max_runs)

            netperf_result_template(result_tcp, tcp_res_data)
            result_tcp.set_comment(pr_comment)
            perf_api.save_result(result_tcp)

        if nperf_protocols.find("udp") > -1 and ("gro", "off") not in setting:
            # prepare PerfRepo result for udp ipv6
            result_udp = perf_api.new_result("udp_ipv6_id",
                                             "udp_ipv6_result",
                                             hash_ignore=[
                                                 'kernel_release',
                                                 'redhat_release'])
            for offload in setting:
                result_udp.set_parameter(offload[0], offload[1])

            if nperf_msg_size is not None:
                result_udp.set_parameter("nperf_msg_size", nperf_msg_size)

            result_udp.set_parameter('netperf_server_on_vlan', vlans[0])
            result_udp.set_parameter('netperf_client_on_vlan', vlans[0])
            result_udp.add_tag(product_name)
            if nperf_mode == "multi":
                result_udp.add_tag("multithreaded")
                result_udp.set_parameter('num_parallel', nperf_num_parallel)

            baseline = perf_api.get_baseline_of_result(result_udp)
            netperf_baseline_template(netperf_cli_udp6, baseline)

            udp_res_data = m2.run(netperf_cli_udp6,
                                  timeout = (netperf_duration + nperf_reserve)*nperf_max_runs)

            netperf_result_template(result_udp, udp_res_data)
            result_udp.set_comment(pr_comment)
            perf_api.save_result(result_udp)

        # for SCTP only gso offload on/off
        if (nperf_protocols.find("sctp") > -1 and
              (len([val for val in setting if val[1] == 'off']) == 0 or
               ('gso', 'off') in setting)):
            result_sctp = perf_api.new_result("sctp_ipv6_id",
                                              "sctp_ipv6_result",
                                              hash_ignore=[
                                                  'kernel_release',
                                                  'redhat_release'])
            for offload in setting:
                result_sctp.set_parameter(offload[0], offload[1])

            result_sctp.set_parameter('netperf_server_on_vlan', vlans[0])
            result_sctp.set_parameter('netperf_client_on_vlan', vlans[0])
            result_sctp.add_tag(product_name)
            if nperf_mode == "multi":
                result_sctp.add_tag("multithreaded")
                result_sctp.set_parameter("num_parallel", nperf_num_parallel)

            baseline = perf_api.get_baseline_of_result(result_sctp)
            netperf_baseline_template(netperf_cli_sctp6, baseline)
            sctp_res_data = m2.run(netperf_cli_sctp6,
                                   timeout = (netperf_duration + nperf_reserve)*nperf_max_runs)

            netperf_result_template(result_sctp, sctp_res_data)
            result_sctp.set_comment(pr_comment)
            perf_api.save_result(result_sctp)

        srv_proc.intr()

#reset offload states
dev_features = ""
for offload in offloads:
    dev_features += " %s %s" % (offload, "on")
m1.run("ethtool -K %s %s" % (m1_phy1.get_devname(), dev_features))
m1.run("ethtool -K %s %s" % (m1_phy2.get_devname(), dev_features))
m2.run("ethtool -K %s %s" % (m2_phy1.get_devname(), dev_features))

if nperf_cpupin:
    m1.run("service irqbalance start")
    m2.run("service irqbalance start")
