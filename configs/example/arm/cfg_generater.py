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
"HMC_2500_1x32",
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

MYCPU = O3CPU

def generate_configs(args, r):
  random.seed(r)
  args.cpu_freq = str(r % 5 + 1) + "GHz"
  # Memory configurations.
  args.mem_type = mem_types[r % len(mem_types)]
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
    cache.size = str(assoc) + 'kB'

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
    if r % 5 == 0:
      # In-order CPU.
      MYCPU = MinorCPU
    else:
      # Out-of-order CPU.
      MYCPU = O3CPU
      #MYCPU.fuPool = Param.FUPool(DefaultFUPool(), "Functional Unit pool")
      num = [1, 2, 4, 6, 8]
      # Int: 1, 2, 4, 6, 8
      MYCPU.fuPool.FUList[0].count = num[random.randrange(5)]
      # IntMultDiv: 1 ~ 4
      MYCPU.fuPool.FUList[1].count = random.randrange(1, 5)
      # FP: 1, 2, 4, 6, 8
      MYCPU.fuPool.FUList[2].count = num[random.randrange(5)]
      # FPMultDiv: 1 ~ 4
      MYCPU.fuPool.FUList[3].count = random.randrange(1, 5)
      if random.randrange(2) == 0:
        # Read: 1, 2, 4, 6, 8
        MYCPU.fuPool.FUList[4].count = num[random.randrange(5)]
        # Write: 1, 2, 3, 4
        MYCPU.fuPool.FUList[7].count = num[random.randrange(5)]
        MYCPU.fuPool.FUList[8].count = 0
      else:
        MYCPU.fuPool.FUList[4].count = 0
        MYCPU.fuPool.FUList[7].count = 0
        # ReadWrite: 1, 2, 4, 6, 8
        MYCPU.fuPool.FUList[8].count = num[random.randrange(5)]
      # SIMD: 1, 2, 4, 6, 8
      MYCPU.fuPool.FUList[5].count = num[random.randrange(5)]
      # Pred SIMD: 1, 2, 3, 4
      MYCPU.fuPool.FUList[6].count = random.randrange(1, 5)
      branchPreds = [O3_ARM_v7a_BP(), O3_ARM_PostK_BP(), O3_ARM_S_BP(),
        ex5_big_BP(), HPI_BP(), LocalBP(), TournamentBP(), BiModeBP(),
        TAGE(), LTAGE_TAGE(), TAGE_SC_L_TAGE(), TAGE_SC_L_TAGE_8KB(),
        LTAGE(), TAGE_SC_L(), MultiperspectivePerceptron(),
        MultiperspectivePerceptron8KB(), MPP_TAGE()
      ]
      MYCPU.branchPred = branchPreds[random.randrange(len(branchPreds))]

  return args
