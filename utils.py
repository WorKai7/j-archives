def convert_date_to_str(date):
        if date.day() < 10:
            if date.month() < 10:
                return str("0" + str(date.day())) + "-0" + str(date.month()) + "-" + str(date.year())
            
            return str("0" + str(date.day())) + "-" + str(date.month()) + "-" + str(date.year())
        
        elif date.month() < 10:
            return str(date.day()) + "-0" + str(date.month()) + "-" + str(date.year())
        
        return str(date.day()) + "-" + str(date.month()) + "-" + str(date.year())


def convert_datestr_to_tuple(date_str):
        day, month, year = date_str.split('-')
        return int(year), int(month), int(day)