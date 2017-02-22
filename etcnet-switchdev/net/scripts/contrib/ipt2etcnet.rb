#!/usr/bin/env ruby
# a script to convert _currently_ active iptables rules as dumped by
# iptables-save into /etc/net "human readable" format as documented
# in http://www.altlinux.org/Etcnet/firewall [ru]
# [still requires additional fixes, on etcnet syntax side too]
# Copyleft 2006 by Michael Shigorin <mike@osdn.org.ua>

module Ipt2etcnet

require "iptables-save.rb"
require "etcnet-fw-syntax.rb"

DEBUG = true
HUMAN_READABLE = false

IPT_SAVE = "/sbin/iptables-save"
#IPT_SAVE = "/bin/cat iptables"
FWOUTDIR = "/etc/net/ifaces/default/fw/iptables"

NEWTABLE = /^\*([a-z]+)$/
NEWCHAIN = /^:([A-Za-z0-9_-]+) ([A-Z-]+) \[(\d+):(\d+)\]$/
NEWRULE = /^-A ([A-Za-z0-9_-]+) (.*)$/
HEADER = /^(# Generated by .*)$/
COMMIT = /^COMMIT$/ 

tables = Iptables.new
chains = Table.new(nil)

# slurp existing rules
# FIXME: exception handling
IO.popen(IPT_SAVE) do |rules|
	rules.each do |line|
		case line
		when NEWTABLE then chains = Table.new($1)	# see appropriate regexp
		when NEWCHAIN then chains.add(Chain.new($1,$2))
		when NEWRULE  then chains[$1].add(Rule.new($2, HUMAN_READABLE))
		when COMMIT   then tables.add(chains.commit)
		end
	end
end

# OK, now flush them out
# FIXME: IO errors handling!
tables.each do |table|
	tabledir = File.join(FWOUTDIR, table.name)		# one dir per table
	`/bin/mkdir -p #{tabledir}`
	table.each do |chain|
		File.open(File.join(tabledir, chain.name), "w") do |f|
			chain.each do |rule|
				f.puts(rule)
			end
		end
	end
end

# FIXME: figure out what's up with other policies
File.open(File.join(FWOUTDIR, "..", "options"), "w") do |f|
	tables["filter"].each do |chain|
		case chain.name
		when "INPUT", "OUTPUT", "FORWARD"
			f.puts("IPTABLES_#{chain.name}_POLICY=#{chain.policy}")
		end
	end
end

#p tables["filter"]

end	# module

### TODO:
# - factor out extra complications with Rule when no 
#   human-readability is requested?
# - getopt
# - package somewhat
# - fix all FIXMEs :-)