package Tutorial {
    public import ScalarValues::*;
    public import SOSA::*;
    
    part def TutorialSystem;        
    part SensorSystem: TutorialSystem {
    
        part TempSensor: TutorialSystem {
            metadata SOSA_Sensor;
        } 

        part TempSample: TutorialSystem {
            attribute currenTemp {@SOSA_ObservableProperty{}}
            metadata SOSA_Sample;
        }
        
        connection SOSA_observes
            connect TempSensor to TempSample.currenTemp;
        
        connection SOSA_isObservedBy
            connect TempSample.currenTemp to TempSensor;
        
    }
}
