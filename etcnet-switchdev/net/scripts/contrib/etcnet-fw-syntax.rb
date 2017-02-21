#!/usr/bin/env ruby
#
# This file is used by ipt2etcnet.rb
#
# cope with /etc/net/ifaces/default/fw/iptables/syntax
# or at least cleanup extra space
# copyleft 2006 Michael Shigorin <mike@osdn.org.ua>

module Ipt2etcnet

SYNTAX = "/etc/net/ifaces/default/fw/iptables/syntax"

COMMENT = /^\s*#/
EMPTY = /^\s*$/
RULE = /^([a-z_-]+):\s*(.+)$/

class Rule < String
	
	@@rmap = Hash.new

	begin
		File.open(SYNTAX) do |f|
			f.readlines.each do |line|
				case line
				when EMPTY, COMMENT 
					next
				when RULE
					human = $1.strip
					iptables = $2.strip
					next if iptables.empty?
					# possibly overwriting
					@@rmap[iptables] = human unless human.empty?
				else
					puts "** malformed syntax line: #{line}"
				end
			end
		end
	end

	# reverse key length sort
	@@rmaps = @@rmap.sort { |a,b| b[0].length <=> a[0].length }
	# pre-fill regexp patterns
	@@rmapx = @@rmaps.collect { |a| a << Regexp.new('\B'+a[0]+'\b') }

	def initialize(rule, to_human = false)
		super(rule.strip)
		if to_human then self.to_human end
	end

	### FIXME: needs proper \B\b fences like to_human
	def to_s
		@@rmap.each do |iptables,human|
			next unless self.gsub!(human,iptables)
		end
		self
	end

	def to_human
		@@rmapx.each do |iptables,human,pattern|
			next unless self.gsub!(pattern,human)
		end
		self
	end

	def Rule.map; @@rmap; end
	def Rule.map_sort; @@rmaps; end
	def Rule.map_regex; @@rmapx; end
end

end	# module
