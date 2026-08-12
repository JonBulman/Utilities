#
# Class definitions
#
# from datetime import date, timedelta
# Used to store Solcast data
#
from jon_bulman_utilities.base import Jon_Bulman_Base

class Solcast_Breakdown:
    def __init__(self, pv_estimate, pv_estimate10, pv_estimate90, period_end, period):
        self.pv_estimate = pv_estimate
        self.pv_estimate10 = pv_estimate10
        self.pv_estimate90 = pv_estimate90
        self.period_end = period_end
        self.period = period
        
        splitdata = period_end.split("T")
        self.date = splitdata[0]
        time_val = splitdata[1].split(":")
        self.from_time = f"{time_val[0]}:{time_val[1]}"
           
    def Date(self):
        return self.date
    
    def Time(self):
        return self.from_time
    
    def PV_Estimate(self, option):
        match option:
            case "p10":
                pvv = self.pv_estimate10
            case "p90":
                pvv = self.pv_estimate90
            case _:
                pvv = self.pv_estimate
        return pvv

    def Solcast_Print(self):
        s = Solcast_Breakdown.Solcast_String(self)
        print(s)

    def Solcast_String(self):
        s = f"Date:{self.date},Time:{self.from_time},pv_estimate={self.pv_estimate},pv_estimate10={self.pv_estimate10},pv_estimate90={self.pv_estimate90}\n"
        return s
         
    def Solcast_HTML_String(self):
        hmtlfmt_start = "<b style=\"color: red;\">"
        end_bold = "</b>"
        line_break = "<br/>"
        if self.pv_estimate > 0.5:
            hmtlfmt_start = "<b style=\"color: green;\">"
        elif self.pv_estimate > 0.:
            hmtlfmt_start = "<b style=\"color: orange;\">"

        s = f"{self.date},{hmtlfmt_start}{self.from_time},{self.pv_estimate:.3f}{end_bold},{self.pv_estimate10:.3f} (p10),{self.pv_estimate90:.3f} (p90){line_break}"
        return s
    
class Solar_PV_Data(Jon_Bulman_Base):
    def __init__(self, date, pv_forecast_solar, pv_solcast, pv_visual_crossing, pv_actual=0.):
        self.date = date
        self.pv_forecast_solar = pv_forecast_solar
        self.pv_solcast = pv_solcast
        self.pv_visual_crossing = pv_visual_crossing
        self.pv_actual = pv_actual
    
    def Date(self):
        return self.date

    def Actual(self, actual):
        self.pv_actual = actual

    def Get_Actual(self):
        return self.pv_actual

    def Print(self):
        s = Solar_PV_Data.String(self)
        print(s)

    def String(self):
        s = f"Date:{self.date},Actual:{self.pv_actual:.3f},Forecast Solar={self.pv_forecast_solar:.3f},Solcast={self.pv_solcast:.3f},Visual Crossing={self.pv_visual_crossing:.3f}\n"
        return s
    
    def CSV(self):
        s = f"{self.date},{self.pv_actual:.3f},{self.pv_forecast_solar:.3f},{self.pv_solcast:.3f},{self.pv_visual_crossing:.3f}\n"
        return s
    
    def HTML_String(self):
        hmtlfmt_start = "<b style=\"color: red;\">"
        end_bold = "</b>"
        line_break = "<br/>"
        if self.pv_actual > 0.5:
            hmtlfmt_start = "<b style=\"color: green;\">"
        elif self.pv_actual > 0.:
            hmtlfmt_start = "<b style=\"color: orange;\">"#

        s = f"{self.date},{hmtlfmt_start},{self.pv_actual:.3f}{self.pv_forecast_solar:.3f}{end_bold}{self.pv_solcast:.3f},{self.pv_visual_crossing:.3f}{line_break}"
        return s