#!/usr/bin/env ruby
#
# This file is used by ipt2etcnet.rb
#
# simple library to accomodate iptables-save data
# Copyleft 2006 by Michael Shigorin <mike@osdn.org.ua>

module Ipt2etcnet

class ArrayExt < Array
	
	def initialize(name = nil)
		@name = name
	end
	
	attr_reader :name
	
	def add(item)	# push another one onto the stack
		self << item
	end
	
	def list	# returns an array of my object names
		collect { |x| x.name }
	end
	
	def [](key)		# Pickaxe example ;-)
		#return self[key] if key.kind_of?(Integer)
		return find { |x| x.name == key }
	end

	def inspect; "<#{name}> #{super}"; end

end


class Iptables < ArrayExt; end


class Table < ArrayExt
	
	def initialize(name)
		super(name)
		@committed = false
	end
	
	attr_reader :committed
	
	def add(chain)
		self << chain unless @committed
	end

	def commit
		@committed = true
		self
	end
	
end


class Chain < ArrayExt
	
	def initialize(name, policy = "ACCEPT")
		super(name)
		@policy = policy
	end
	
	attr_reader :policy
	
end

end	# module
