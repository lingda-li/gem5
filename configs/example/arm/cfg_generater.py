import random
import m5
from m5.params import *
from m5.objects import *
from m5.objects.FUPool import *
from m5.objects.BranchPredictor import *
m5.util.addToPath('../../')
from common.Caches import *
import devices
from common.cores.arm.O3_ARM_v7a import O3_ARM_v7a_BP, O3_ARM_PostK_BP, O3_ARM_S_BP
from common.cores.arm.ex5_big import ex5_big_BP
from common.cores.arm.HPI import HPI_BP


mem_types = [
"DDR3_1600_8x8",
#"HMC_2500_1x32",
"DDR3_2133_8x8",
"DDR4_2400_16x4",
"DDR4_2400_8x8",
"DDR4_2400_4x16",
"LPDDR2_S4_1066_1x32",
"WideIO_200_1x128",
"LPDDR3_1600_1x32",
"GDDR5_4000_2x32",
"HBM_1000_4H_1x128",
"HBM_1000_4H_1x64",
"LPDDR5_5500_1x16_BG_BL32",
"LPDDR5_5500_1x16_BG_BL16",
"LPDDR5_5500_1x16_8B_BL32",
"LPDDR5_6400_1x16_BG_BL32",
"LPDDR5_6400_1x16_BG_BL16",
"LPDDR5_6400_1x16_8B_BL32"
]

def generate_configs(args, r):
  random.seed(r)
  args = args
  #args.cpu_freq = str(r % 5 + 1) + "GHz"
  freqs = ["1GHz", "2GHz", "2.5GHz", "3.3333GHz", "5GHz"]
  args.cpu_freq = freqs[r % 5]
  # Memory configurations.
  args.mem_type = mem_types[r % len(mem_types)]
  print("Mem", args.mem_type)
  if r % 4 == 0:
    args.mem_channels = 1
  elif r % 4 == 1:
    args.mem_channels = 4
  else:
    args.mem_channels = 2
  #args.mem_ranks

  # Cache configurations.
  for cache in [devices.L1I, devices.L1D, devices.L2]:
    # Latency and size.
    if cache == devices.L2:
      # 8 ~ 23
      l = r % 16 + 8
      # 4 ~ 32
      assoc = 2 ** (r % 4 + 2)
      # 64 ~ 256
      sets = 2 ** (r % 3 + 6)
      if r % 2 == 0:
        cache.clusivity='mostly_excl'
      else:
        cache.clusivity='mostly_incl'
    else:
      # 1 ~ 4
      l = r % 4 + 1
      # 2, 3, 4
      assoc = r % 3 + 2
      # 4 ~ 16
      sets = 2 ** (r % 3 + 2)
    cache.tag_latency = l
    cache.data_latency = l
    cache.response_latency = l // 2 + 1
    cache.assoc = assoc
    cache.size = str(sets * assoc) + 'kB'

    # MSHR etc.
    p = r % 4
    if cache == devices.L1I:
      # 1 ~ 8
      cache.mshrs = 2 ** p
    elif cache == devices.L1D:
      # 4 ~ 32
      cache.mshrs = 2 ** (p + 2)
      # 4 ~ 16
      cache.write_buffers = 2 ** (r % 3 + 2)
    else:
      # 8 ~ 64
      cache.mshrs = 2 ** (p + 3)
      # 8 ~ 32
      cache.write_buffers = 2 ** (r % 3 + 3)
    # 4, 8, 12, 16, 20
    cache.tgts_per_mshr = 4 + 4 * (r % 5)

  # CPU.
  if args.cpu == "minor":
    # In-order CPU.
    base_width = random.randrange(1, 4)
    # 1 ~ 2
    MinorCPU.fetch1FetchLimit = random.randrange(1, 3)
    ## 0
    #MinorCPU.fetch1LineSnapWidth
    ## 0
    #MinorCPU.fetch1LineWidth
    # 1 ~ 3
    #MinorCPU.fetch1ToFetch2ForwardDelay = random.randrange(1, 4)
    MinorCPU.fetch1ToFetch2ForwardDelay = 1
    # 1 ~ 2
    MinorCPU.fetch1ToFetch2BackwardDelay = random.randrange(1, 3)
    # 1 ~ 3
    MinorCPU.fetch2InputBufferSize = base_width
    # 1 ~ 2
    MinorCPU.fetch2ToDecodeForwardDelay = random.randrange(1, 3)
    # 1 ~ 3
    MinorCPU.decodeInputBufferSize = base_width
    # 1 ~ 3
    MinorCPU.decodeToExecuteForwardDelay = random.randrange(1, 4)
    # 1 ~ 3
    MinorCPU.decodeInputWidth = base_width
    # 1 ~ 3
    MinorCPU.executeInputWidth = base_width
    # 1 ~ 3
    MinorCPU.executeIssueLimit = base_width
    # 1 ~ 2
    MinorCPU.executeMemoryIssueLimit = random.randrange(1, 3)
    # 1 ~ 3
    MinorCPU.executeCommitLimit = base_width
    # 1 ~ 2
    MinorCPU.executeMemoryCommitLimit = min(random.randrange(1, 3), base_width)
    # 5 ~ 10
    MinorCPU.executeInputBufferSize = random.randrange(1, 3) * 5
    # 1 ~ 4
    MinorCPU.executeMaxAccessesInMemory = random.randrange(1, 5)
    # 1 ~ 2
    MinorCPU.executeLSQMaxStoreBufferStoresPerCycle = random.randrange(1, 3)
    # 1 ~ 2
    MinorCPU.executeLSQRequestsQueueSize = MinorCPU.executeMemoryCommitLimit
    # 1 ~ 4
    MinorCPU.executeLSQTransfersQueueSize = MinorCPU.executeMaxAccessesInMemory
    # 4, 8, 12
    MinorCPU.executeLSQStoreBufferSize = random.randrange(1, 4) * 4
    # 1 ~ 2
    MinorCPU.executeBranchDelay = random.randrange(1, 3)
    print("InOrder", base_width)

    # Functional units.
    MinorCPU.executeFuncUnits.funcUnits = []
    # Int: 1 ~ 3
    for i in range(random.randrange(1, 4)):
      MinorCPU.executeFuncUnits.funcUnits.append(MinorDefaultIntFU())
    # IntMult: 1 ~ 2
    for i in range(random.randrange(1, 3)):
      MinorCPU.executeFuncUnits.funcUnits.append(MinorDefaultIntMulFU())
    # IntDiv: 1
    MinorCPU.executeFuncUnits.funcUnits.append(MinorDefaultIntDivFU())
    # FP & SIMD: 1 ~ 3
    for i in range(random.randrange(1, 4)):
      MinorCPU.executeFuncUnits.funcUnits.append(MinorDefaultFloatSimdFU())
    # Pred: 1
    MinorCPU.executeFuncUnits.funcUnits.append(MinorDefaultPredFU())
    # Mem: 1 ~ 2
    for i in range(random.randrange(1, 3)):
      MinorCPU.executeFuncUnits.funcUnits.append(MinorDefaultMemFU())
    # Misc: 1
    MinorCPU.executeFuncUnits.funcUnits.append(MinorDefaultMiscFU())
  elif args.cpu == "o3":
    # Out-of-order CPU.
    # Functional units.
    num = [1, 2, 4, 6, 8]
    # Int: 1, 2, 4, 6, 8
    O3CPU.fuPool.FUList[0].count = num[random.randrange(5)]
    # IntMultDiv: 1 ~ 4
    O3CPU.fuPool.FUList[1].count = random.randrange(1, 5)
    # FP: 1, 2, 4, 6, 8
    O3CPU.fuPool.FUList[2].count = num[random.randrange(5)]
    # FPMultDiv: 1 ~ 4
    O3CPU.fuPool.FUList[3].count = random.randrange(1, 5)
    if random.randrange(2) == 0:
      # Read: 1, 2, 4, 6, 8
      O3CPU.fuPool.FUList[4].count = num[random.randrange(5)]
      # Write: 1, 2, 3, 4
      O3CPU.fuPool.FUList[7].count = num[random.randrange(5)]
      O3CPU.fuPool.FUList[8].count = 0
    else:
      O3CPU.fuPool.FUList[4].count = 0
      O3CPU.fuPool.FUList[7].count = 0
      # ReadWrite: 1, 2, 4, 6, 8
      O3CPU.fuPool.FUList[8].count = num[random.randrange(5)]
    # SIMD: 1, 2, 4, 6, 8
    O3CPU.fuPool.FUList[5].count = num[random.randrange(5)]
    # Pred SIMD: 1, 2, 3, 4
    O3CPU.fuPool.FUList[6].count = random.randrange(1, 5)

    # Buffers.
    #O3CPU.numRobs
    sizes = [32, 64, 96, 128, 160, 192]
    base_size = sizes[random.randrange(len(sizes))]
    # 32, 64, 96, 128, 192, 256
    O3CPU.numPhysIntRegs = max(min(base_size, sizes[random.randrange(len(sizes))]), 48)
    # ~ 256
    O3CPU.numPhysFloatRegs = max(min(base_size, sizes[random.randrange(len(sizes))]), 48)
    # ~ 256
    O3CPU.numPhysVecRegs = max(min(base_size, sizes[random.randrange(len(sizes))]), 48)
    # ~ 32
    sizes = [24, 28, 32]
    O3CPU.numPhysVecPredRegs = sizes[random.randrange(len(sizes))]
    # ~ 256. May not need to set.
    #O3CPU.numPhysCCRegs
    # 8 ~ 64
    sizes = [8, 16, 32, 48, 64]
    O3CPU.numIQEntries = sizes[random.randrange(len(sizes))]
    # 32 ~ 192
    O3CPU.numROBEntries = base_size
    # 8, 16, 24, 32
    sizes = [8, 16, 24, 32]
    O3CPU.LQEntries = sizes[random.randrange(len(sizes))]
    # ~ 32
    O3CPU.SQEntries = sizes[random.randrange(len(sizes))]
    # 16 ~ 32
    O3CPU.fetchQueueSize = 16 * random.randrange(1, 3)
    print("O3", base_size, O3CPU.numIQEntries, O3CPU.numPhysIntRegs, O3CPU.numPhysFloatRegs, O3CPU.numPhysVecRegs)

    # Widths.
    front_width = random.randrange(1, 9)
    # 1 ~ 8
    O3CPU.fetchWidth = front_width
    # 1 ~ 8
    O3CPU.decodeWidth = min(front_width + (random.randrange(0, 3) // 2), 8)
    # 1 ~ 8
    O3CPU.renameWidth = min(front_width + (random.randrange(0, 3) // 2), 8)
    back_width = random.randrange(1, 9)
    # 1 ~ 8
    O3CPU.dispatchWidth = back_width
    # 1 ~ 8
    O3CPU.issueWidth = min(back_width + random.randrange(0, 3), 8)
    # 1 ~ 8
    O3CPU.wbWidth = O3CPU.issueWidth
    # 1 ~ 8
    O3CPU.commitWidth = min(back_width + random.randrange(0, 3), 8)
    # 1 ~ 20
    O3CPU.squashWidth = O3CPU.commitWidth + random.randrange(0, 4) * 4
    print("Width", front_width, back_width)

    # Latencies.
    back_lat = 1
    # 1 ~ 2
    O3CPU.decodeToFetchDelay = back_lat
    # 1 ~ 2
    O3CPU.renameToFetchDelay = back_lat
    # 1 ~ 2
    O3CPU.iewToFetchDelay = back_lat
    # 1 ~ 2
    O3CPU.commitToFetchDelay = back_lat
    # 1 ~ 2
    O3CPU.renameToDecodeDelay = back_lat
    # 1 ~ 2
    O3CPU.iewToDecodeDelay = back_lat
    # 1 ~ 2
    O3CPU.commitToDecodeDelay = back_lat
    # 1 ~ 3
    O3CPU.fetchToDecodeDelay = random.randrange(1, 4)
    # 1 ~ 2
    O3CPU.iewToRenameDelay = back_lat
    # 1 ~ 2
    O3CPU.commitToRenameDelay = back_lat
    # 1 ~ 3
    O3CPU.decodeToRenameDelay = random.randrange(1, 4)
    # 1 ~ 2
    O3CPU.commitToIEWDelay = back_lat
    # 1 ~ 3
    O3CPU.renameToIEWDelay = random.randrange(1, 4)
    # 1 ~ 2
    O3CPU.issueToExecuteDelay = random.randrange(1, 3)
    # 1 ~ 2
    O3CPU.iewToCommitDelay = random.randrange(1, 3)
    # 1 ~ 2
    #O3CPU.renameToROBDelay = random.randrange(1, 3)
    O3CPU.renameToROBDelay = 1
    # 10 ~ 30
    O3CPU.trapLatency = random.randrange(2, 7) * 5
    # 1 ~ 2
    O3CPU.fetchTrapLatency = back_lat
  else:
    raise RuntimeError("Unsupported CPU type.")

  # Branch prediction.
  branchPreds = [O3_ARM_v7a_BP, O3_ARM_PostK_BP, O3_ARM_S_BP,
    ex5_big_BP, HPI_BP, LocalBP, TournamentBP, BiModeBP,
    TAGE, LTAGE, TAGE_SC_L_64KB, TAGE_SC_L_8KB,
    MultiperspectivePerceptron8KB, MultiperspectivePerceptron64KB,
    MultiperspectivePerceptronTAGE64KB, MultiperspectivePerceptronTAGE8KB
  ]
  branchPred = branchPreds[random.randrange(len(branchPreds))]
  print("branchPred", branchPred)

  return args, branchPred
