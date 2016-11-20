data Position = Position Int Int

instance Show Position where
  show (Position a b) = (show a) ++ " " ++ (show b)

readPos :: [String] -> Position
readPos [a,b] = Position (read a::Int) (read b::Int)

data Vessel = Ship Position | Submarine Position deriving Show

data Event = Spawn
           | Die
           | Hit Position
           | Miss Position
           | Move Position
           deriving Show

type Action = (Vessel, Event)

data Round = Shipround | Submarineround | Init deriving Eq




parseShot :: [String] -> (Position -> Event) -> Action
parseShot arguments vessel = (Submarine origin, vessel target)
  where
    origin = readPos $ take 2 arguments
    target = readPos $ drop 2 arguments


-- Returns an action if any happened on this line and the new Round
parseLine :: Round -> String -> (Maybe Action, Round)
parseLine round s =
  let
    keyword = head $ words s
    arguments = tail $ words s
  in
    case keyword of
      "SHIPSTART"            -> (Just (Ship (Position 0 0), Spawn), round)
      "SUBMARINESTART"       -> (Just (Submarine (Position 0 0), Spawn), round)
      "STARTROUNDSHIP"       -> (Nothing, Shipround)
      "STARTROUNDSUBMARINE"  -> (Nothing, Submarineround)
      "MOVE"                 -> (Just action, round)
                                where
                                  origin = readPos $ take 2 arguments
                                  target = readPos $ drop 2 arguments
                                  vessel = (if round == Shipround then Ship else Submarine) origin
                                  action = (vessel, Move target)
      "HIT"                  -> (Just (parseShot arguments Hit), round)
      "MISS"                 -> (Just (parseShot arguments Miss), round)



--parseLog :: String -> [Action]
