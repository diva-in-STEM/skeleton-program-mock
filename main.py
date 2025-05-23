import datetime
import os
import random

BLANK = "   "
while True:
  try:
    MAX_Q_SIZE = int(input("Enter the maximum queue size (must be a positive integer): "))
    TILL_SPEED = int(input("Enter the till speed (must be an integer > 0): "))
    if MAX_Q_SIZE >= 1 and TILL_SPEED > 0:
      break
  except:
    print("You must enter an integer value. Try again.")
  

MAX_TILLS = 5
MAX_TIME = 50

TIME_IDLE = 0
TIME_BUSY = 1
TIME_SERVING = 2
IS_BROKEN = 3
REPAIR_TIME = 4

ARRIVAL_TIME = 0
ITEMS = 1

# indices for Stats data structure
MAX_Q_LENGTH = 0
MAX_WAIT = 1
TOTAL_WAIT = 2
TOTAL_Q = 3
TOTAL_Q_OCCURRENCE = 4
TOTAL_NO_WAIT = 5
TOTAL_TILL_BREAKDOWNS = 6

class Q_Node:
  def __init__(self):
    self.BuyerID = BLANK
    self.WaitingTime = 0
    self.ItemsInBasket = 0
    self.Priority = 0

FileNames = []

def getDataFiles():
  for fname in os.listdir():
    if fname.__contains__("SimulationData") and fname.__contains__(".txt"):
      FileNames.append(fname)

getDataFiles()
print(FileNames)

def ResetDataStructures():
  Stats = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
  Tills = [[0, 0, 0, 0, 0] for i in range(MAX_TILLS + 1)]
  BuyerQ = [Q_Node() for i in range(MAX_Q_SIZE)]
  return Stats, Tills, BuyerQ

def ChangeSettings():
  SimulationTime = 10
  NoOfTills = 2
  print("Settings set for this simulation:")
  print("=================================")
  print(f"Simulation time: {SimulationTime}")
  print(f"Tills operating: {NoOfTills}")
  print("=================================")
  print()
  Answer = input("Do you wish to change the settings?  Y/N: ")
  if Answer.upper() == 'Y':
    print(f"Maximum simulation time is {MAX_TIME} time units")
    while True:
      try:
        SimulationTime = int(input("Simulation run time: "))
        while SimulationTime > MAX_TIME or SimulationTime < 1:
          print(f"Maximum simulation time is {MAX_TIME} time units")
          SimulationTime = int(input("Simulation run time: "))
        break
      except:
        print("Must be an integer")

    print(f"Maximum number of tills is {MAX_TILLS}")
    while True:
      try:
        NoOfTills = int(input("Number of tills in use: "))
        while NoOfTills > MAX_TILLS or NoOfTills < 1:
          print(f"Maximum number of tills is {MAX_TILLS}")
          NoOfTills = int(input("Number of tills in use: "))
        break
      except:
        print("Must be an integer")
  return SimulationTime, NoOfTills

def ReadInSimulationData(FileName):
  Data = [[0, 0] for i in range(MAX_TIME + 1)]

  try: 
    FileIn = open(FileName, 'r')
    firstChar = FileIn.read(1)
    if not firstChar:
      exit()

    FileIn.seek(0)
  except:
    print("Unable to open simulation data file or it was empty!")
    exit()

  DataString = FileIn.readline()
  Count = 0
  while DataString != "" and Count < MAX_TIME:
    Count += 1
    try:
      Data[Count][ARRIVAL_TIME] = int(DataString[0])
      
      ItemsInBasket = int(DataString[2:])
      Data[Count][ITEMS] =  ItemsInBasket
    except:
      print(f"Invalid data type in simulation data file on line {Count}!")
      exit()
    DataString = FileIn.readline()
  FileIn.close()
  return Data

def OutputHeading():
  print()
  print("Time Buyer  | Start Till Serve | Till Time Time Time |      Queue")
  print("     enters | serve      time  | num- idle busy ser- | Buyer Wait Items")
  print("     (items)| buyer            | ber            ving | ID    time in")
  print("            |                  |                     |            basket")

def BuyerJoinsQ(Data, BuyerQ, QLength, BuyerNumber, TotalItemsSold):
  ItemsInBasket = Data[BuyerNumber][ITEMS]
  BuyerQ[QLength].BuyerID = f"B{BuyerNumber}"
  BuyerQ[QLength].ItemsInBasket  = ItemsInBasket
  if ItemsInBasket > 15:
    queued = False
    while not queued:
      pos = QLength
      if pos == 0:
        queued = True
      elif BuyerQ[pos - 1].ItemsInBasket <= 15:
        BuyerQ[pos - 1], BuyerQ[pos] = BuyerQ[pos], BuyerQ[pos - 1]
      else:
        queued = True
          
  TotalItemsSold += ItemsInBasket
  QLength += 1
  return BuyerQ, QLength, TotalItemsSold

def BuyerArrives(Data, BuyerQ, QLength, BuyerNumber, NoOfTills, Stats, Turnaways, TotalItemsSold, TotalBuyers):
  print(f"  B{BuyerNumber}({Data[BuyerNumber][ITEMS]})")
  if QLength < MAX_Q_SIZE-1:
    BuyerQ, QLength, TotalItemsSold = BuyerJoinsQ(Data, BuyerQ, QLength, BuyerNumber, TotalItemsSold)
    TotalBuyers += 1
  else:
    Turnaways += 1
  return BuyerQ, QLength, NoOfTills, Stats, Turnaways, TotalItemsSold, TotalBuyers

def FindFreeTill(Tills, NoOfTills):
  FoundFreeTill = False
  TillNumber = 0
  while not FoundFreeTill and TillNumber < NoOfTills:
    TillNumber += 1
    if Tills[TillNumber][IS_BROKEN] == 0 and Tills[TillNumber][TIME_SERVING] == 0:
      FoundFreeTill = True
  if FoundFreeTill:
    return TillNumber
  else:
    return -1

def ServeBuyer(BuyerQ, QLength):
  ThisBuyerID = BuyerQ[0].BuyerID
  ThisBuyerWaitingTime = BuyerQ[0].WaitingTime
  ThisBuyerItems = BuyerQ[0].ItemsInBasket
  for Count in range(QLength):
    BuyerQ[Count].BuyerID = BuyerQ[Count + 1].BuyerID
    BuyerQ[Count].WaitingTime = BuyerQ[Count + 1].WaitingTime
    BuyerQ[Count].ItemsInBasket = BuyerQ[Count + 1].ItemsInBasket
  BuyerQ[QLength].BuyerID = BLANK
  BuyerQ[QLength].WaitingTime = 0
  BuyerQ[QLength].ItemsInBasket = 0
  QLength -= 1
  print(f"{ThisBuyerID:>17s}", end='')
  return BuyerQ, QLength, ThisBuyerID, ThisBuyerWaitingTime, ThisBuyerItems

def UpdateStats(Stats, WaitingTime):
  Stats[TOTAL_WAIT] += WaitingTime
  if WaitingTime > Stats[MAX_WAIT]:
    Stats[MAX_WAIT] = WaitingTime
  if WaitingTime == 0:
    Stats[TOTAL_NO_WAIT] += 1
  return Stats

def CalculateServingTime(Tills, ThisTill, NoOfItems):
  ServingTime = (NoOfItems // TILL_SPEED) + 1
  Tills[ThisTill][TIME_SERVING] = ServingTime
  print(f"{ThisTill:>5d}{ServingTime:>5d}")
  return Tills

def IncrementTimeWaiting(BuyerQ, QLength, Tills, Stats):
  if random.randint(1, 100) <= 5:
    BrokenTillIndex = random.randint(1, len(Tills) - 1)
    if Tills[BrokenTillIndex][IS_BROKEN] == 0:
      Tills[BrokenTillIndex][IS_BROKEN] = 1
      Tills[BrokenTillIndex][REPAIR_TIME] = random.randint(3, 6)
      print(f"!! Till {BrokenTillIndex} has broken down! Repair time: {Tills[BrokenTillIndex][4]}")
      Stats[TOTAL_TILL_BREAKDOWNS] += 1
  
  for Count in range(QLength):
    BuyerQ[Count].WaitingTime += 1

  return BuyerQ, Stats

def UpdateTills(Tills, NoOfTills):
  for TillNumber in range(1, NoOfTills + 1):
    if Tills[TillNumber][IS_BROKEN] == 1:
      Tills[TillNumber][REPAIR_TIME] -= 1
      if Tills[TillNumber][REPAIR_TIME] <= 0:
        Tills[TillNumber][IS_BROKEN] = 0
        print(f"!! Till {TillNumber} has been repaired and is back in service!")
    else:
      if Tills[TillNumber][TIME_SERVING] == 0:
        Tills[TillNumber][TIME_IDLE] += 1
      else:
        Tills[TillNumber][TIME_BUSY] += 1
        Tills[TillNumber][TIME_SERVING] -= 1
  return Tills

def OutputTillAndQueueStates(Tills, NoOfTills, BuyerQ, QLength):
  for i in range(1, NoOfTills + 1):
    print(f"{i:>34d}{Tills[i][TIME_IDLE]:>6d}{Tills[i][TIME_BUSY]:>6d}{Tills[i][TIME_SERVING]:>6d}")
  print("                                                       ** Start of queue **")
  for i in range(QLength):
    print(f"{BuyerQ[i].BuyerID:>57s}{BuyerQ[i].WaitingTime:>17d}{BuyerQ[i].ItemsInBasket:>6d}")
  print("                                                       *** End of queue ***")
  print("------------------------------------------------------------------------")

def Serving(Tills, NoOfTills, BuyerQ, QLength, Stats):
  TillFree = FindFreeTill(Tills, NoOfTills)
  while TillFree != -1 and QLength > 0:
    BuyerQ, QLength, BuyerID, WaitingTime, ItemsInBasket = ServeBuyer(BuyerQ, QLength)
    Stats = UpdateStats(Stats, WaitingTime)
    Tills = CalculateServingTime(Tills, TillFree, ItemsInBasket)
    TillFree = FindFreeTill(Tills, NoOfTills)
  BuyerQ, Stats = IncrementTimeWaiting(BuyerQ, QLength, Tills, Stats)
  Tills = UpdateTills(Tills, NoOfTills)
  if QLength > 0:
    Stats[TOTAL_Q_OCCURRENCE] += 1 
    Stats[TOTAL_Q] += QLength 
  if QLength > Stats[MAX_Q_LENGTH]:
    Stats[MAX_Q_LENGTH] = QLength
  OutputTillAndQueueStates(Tills, NoOfTills, BuyerQ, QLength)
  return  Tills, NoOfTills, BuyerQ, QLength, Stats

def TillsBusy(Tills, NoOfTills):
  IsBusy = False
  TillNumber = 0
  while not IsBusy and TillNumber <= NoOfTills:
    if Tills[TillNumber][TIME_SERVING] > 0:
      IsBusy = True
    TillNumber += 1
  return IsBusy

def OutputStats(Stats, BuyerNumber, SimulationTime, NoOfTills, Turnaways, TotalItemsSold, TotalBuyers, message):
  OutputFile = "sim_output.txt"
  AverageWaitingTime = round(Stats[TOTAL_WAIT] / BuyerNumber, 1)
  if Stats[TOTAL_Q_OCCURRENCE] > 0:
    AverageQLength = round(Stats[TOTAL_Q] / Stats[TOTAL_Q_OCCURRENCE], 2)
  else:
    AverageQLength = 0
  with open(OutputFile, 'a') as f:
    f.write(f"Simulation from {datetime.datetime.now().strftime("%d/%m/%y, %H:%M")}:")
    f.write(f"""
============================== {message}
The maximum queue length was: {Stats[MAX_Q_LENGTH]} buyers
The maximum waiting time was: {Stats[MAX_WAIT]} time units
{BuyerNumber} buyers arrived during {SimulationTime} time units
The average waiting time was: {AverageWaitingTime} time units
The average queue length was: {AverageQLength} buyers
{Stats[TOTAL_NO_WAIT]} buyers did not need to queue
{Turnaways} buyers were turned away as the queue was full
Sold an average of {round(TotalItemsSold/TotalBuyers, 2)} items per customer
Total till breakdowns was: {Stats[TOTAL_TILL_BREAKDOWNS]}
==============================
With settings:
Number of tills: {NoOfTills}
Simulation time: {SimulationTime} time units
==============================\n
""")

def QueueSimulator(FileName, BuyerNumber, QLength, Stats, Tills, BuyerQ, SimulationTime, NoOfTills):
  Data = ReadInSimulationData(FileName)
  OutputHeading()
  Turnaways = 0
  TotalItemsSold = 0
  TotalBuyers = 0
  TimeToNextArrival = Data[BuyerNumber + 1][ARRIVAL_TIME]
  for TimeUnit in range(SimulationTime):
    TimeToNextArrival -= 1
    print(f"{TimeUnit:>3d}", end='')
    if TimeToNextArrival == 0:
      BuyerNumber += 1
      BuyerQ, QLength, NoOfTills, Stats, Turnaways, TotalItemsSold, TotalBuyers = BuyerArrives(Data, BuyerQ, QLength, BuyerNumber, NoOfTills, Stats, Turnaways, TotalItemsSold, TotalBuyers)
      TimeToNextArrival = Data[BuyerNumber + 1][ARRIVAL_TIME]
    else:
      print()
    Tills, NoOfTills, BuyerQ, QLength, Stats = Serving(Tills, NoOfTills, BuyerQ, QLength, Stats)
  ExtraTime = 0
  while QLength > 0:
    TimeUnit = SimulationTime + ExtraTime
    print(f"{TimeUnit:>3d}")
    Tills, NoOfTills, BuyerQ, QLength, Stats = Serving(Tills, NoOfTills, BuyerQ, QLength, Stats)
    ExtraTime += 1
  while TillsBusy(Tills, NoOfTills):
    TimeUnit = SimulationTime + ExtraTime
    print(f"{TimeUnit:>3d}")
    Tills = UpdateTills(Tills, NoOfTills)
    OutputTillAndQueueStates(Tills, NoOfTills, BuyerQ, QLength)
    ExtraTime += 1
  OutputStats(Stats, BuyerNumber, SimulationTime, NoOfTills, Turnaways, TotalItemsSold, TotalBuyers, "")
  return Stats, BuyerNumber, SimulationTime, NoOfTills, Turnaways, TotalItemsSold, TotalBuyers

if __name__ == "__main__":
  StartBuyerNumber = 0
  StartQLength = 0
  StartStats, StartTills, StartBuyerQ = ResetDataStructures()
  StartSimulationTime, StartNoOfTills = ChangeSettings()

  avgStats = [0] * 10
  avgBuyerNumber = 0
  avgSimulationTime = 0
  avgNoOfTills = 0
  avgTurnaways = 0
  avgTotalItemsSold = 0
  avgTotalBuyers = 0

  for FileName in FileNames:
    Stats, BuyerNumber, SimulationTime, NoOfTills, Turnaways, TotalItemsSold, TotalBuyers = QueueSimulator(
      FileName, StartBuyerNumber, StartQLength, StartStats, StartTills, StartBuyerQ, StartSimulationTime, StartNoOfTills
    )
    avgStats = [x + y for x, y in zip(avgStats, Stats)]
    avgBuyerNumber += BuyerNumber
    avgSimulationTime += SimulationTime
    avgNoOfTills = NoOfTills
    avgTurnaways += Turnaways
    avgTotalItemsSold += TotalItemsSold
    avgTotalBuyers += TotalBuyers

  totalSimulations = len(FileNames)

  avgStats = [round(x / totalSimulations, 2) for x in avgStats]
  avgBuyerNumber = round(avgBuyerNumber / totalSimulations, 2)
  avgSimulationTime = round(avgSimulationTime / totalSimulations, 2)
  avgTurnaways = round(avgTurnaways / totalSimulations, 2)
  avgTotalItemsSold = round(avgTotalItemsSold / totalSimulations, 2)
  avgTotalBuyers = round(avgTotalBuyers / totalSimulations, 2)

  OutputStats(avgStats, avgBuyerNumber, avgSimulationTime, avgNoOfTills, avgTurnaways, avgTotalItemsSold, avgTotalBuyers,
              f"Average of last {totalSimulations} simulations")

  input("Press Enter to finish")

