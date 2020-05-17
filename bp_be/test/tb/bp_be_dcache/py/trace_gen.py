#
#   trace_gen.py
#

import numpy as np

class TraceGen:

  # constructor
  def __init__(self, ptag_width_p, page_offset_width_p, opcode_width_p, data_width_p):
    self.ptag_width_p = ptag_width_p
    self.page_offset_width_p = page_offset_width_p
    self.opcode_width_p = opcode_width_p
    self.data_width_p = data_width_p
    self.packet_len = ptag_width_p + page_offset_width_p + opcode_width_p + data_width_p + 1 # A bit is added to denote cached/uncached accesses

  # print header
  def print_header(self):
    header = "# generated by trace_gen.py \n"
    header += "# packet_len = " + str(self.packet_len) + "\n" 
    return header

  # send load
  # signed: sign extend or not
  # size: load size in bytes
  # page_offset: dcache pkt page offset
  def send_load(self, signed, size, page_offset, ptag, uncached):
    packet = "0001_"
    
    if(uncached):
      packet += "1_"
    else:
      packet += "0_"

    packet += format(ptag, "0"+str(self.ptag_width_p)+"b") + "_"

    if (size == 8):
      packet += "0011_"
    else:
      if (signed):
        if (size == 1):
          packet+= "0000_"
        elif (size == 2):
          packet += "0001_"
        elif (size == 4):
          packet += "0010_"
        else:
          raise ValueError("unexpected size for signed load.")
      else:
        if (size == 1):
          packet += "0100_"
        elif (size == 2):
          packet += "0101_"
        elif (size == 4):
          packet += "0110_"
        else:
          raise ValueError("unexpected size for unsigned load.")

    packet += format(page_offset, "0"+str(self.page_offset_width_p)+"b") + "_"
    packet += format(0, "064b") + "\n" 
    return packet

  # send store
  # signed: sign extend or not
  # size: store size in bytes
  # page_offset: dcache pkt page offset
  def send_store(self, size, page_offset, ptag, uncached, data):
    packet = "0001_"

    if(uncached):
      packet += "1_"
    else:
      packet += "0_"

    packet += format(ptag, "0"+str(self.ptag_width_p)+"b") + "_"
    
    if (size == 1):
      packet += "1000_"
    elif (size == 2):
      packet += "1001_"
    elif (size == 4):
      packet += "1010_"
    elif (size == 8):
      packet += "1011_"
    else:
      raise ValueError("unexpected size for store.")
    
    packet += format(page_offset, "0" + str(self.page_offset_width_p) + "b") + "_"
    packet += format(data, "064b") + "\n"
    return packet

  # receive data
  # data: expected data
  def recv_data(self, data):
    packet = "0010_"
    bin_data = np.binary_repr(data, 64)
    packet += "0" + "0"*(self.ptag_width_p) + "_" + "0"*(self.opcode_width_p) + "_" + "0"*(self.page_offset_width_p) + "_" + bin_data + "\n"
    return packet

  # wait for a number of cycles
  # num_cycles: number of cycles to wait.
  def wait(self, num_cycles):
    command = "0110_" + format(num_cycles, "0" + str(self.packet_len) + "b") + "\n"
    command += "0101_" + (self.packet_len)*"0" + "\n"
    return command

  # finish trace
  def test_finish(self):
    command = "# FINISH \n"
    command += self.wait(8)
    command += "0100_" + (self.packet_len)*"0" + "\n"
    return command

  def test_done(self):
    command = "# DONE \n"
    command += self.wait(8)
    command += "0011_" + (self.packet_len)*"0" + "\n"
    return command

  # wait for a single cycle
  def nop(self):
    return "0000_" + "0"*(self.packet_len) + "\n"
  
  # print comments in the trace file
  def print_comment(self, comment):
    return "# " + comment + "\n"