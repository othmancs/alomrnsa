to_19 = (u'صفر',u'واحد',u'إثنان',u'ثلاثة',u'أربعة',u'خمسة',u'ستة',u'سبعة',u'ثمانية',u'تسعة',u'عشرة',u'أحدعشر',u'إثناعشر',u'ثلاثةعشر',u'أربعةعشر',u'خمسةعشر',u'ستةعشر',u'سبعةعشر',u'ثمانيةعشر',u'تسعةعشر')
tens  = (u'عشرون',u'ثلاثون',u'أربعون',u'خمسون',u'ستون',u'سبعون',u'ثمانون',u'تسعون')
hundreds=('',u'مائـة',u'مائتـان',u'ثلاثمـائة',u'أربعمـائة',u'خمسمـائة',u'ستمائة',u'سبعمائة',u'ثمانمائة',u'تسعمائة')
thousands = ('',u'الف',u'مليون',u'مليار',u'تريليون')

# convert a value < 100 to English.
def _convert_tens(val):
    if val < 20:
        return to_19[val]
    for (dcap, dval) in ((k, 20 + (10 * v)) for (v, k) in enumerate(tens)):
        if dval + 10 > val:
            if val % 10:
                return  to_19[val % 10]+u' و ' +dcap 
            return dcap

# convert a value < 1000 to english, special cased because it is the level that kicks 
# off the < 100 special case.  The rest are more general.  This also allows you to
# get strings in the form of 'forty-five hundred' if called directly.
def _convert_handreds(val):
    word = ''
    (mod, rem) = (val % 100, val // 100)
    if rem > 0:
        word = mod > 0 and hundreds[rem] + u' و ' or  hundreds[rem] 

    if mod > 0:
        word = word+' '+_convert_tens(mod)
    return word

def english_number(val):
    if val < 1000:
        return val < 100 and _convert_tens(val) or  _convert_handreds(val)
    
    for (didx, dval) in ((v - 1, 1000 ** v) for v in range(len(thousands))):
        if dval > val:
            mod = 1000 ** didx
            l = val // mod
            r = val - (l * mod)
            ret = _convert_handreds(l)  +' '+ thousands[didx]
            ret = r > 0 and ret + ' '+u' و ' + english_number(r) or ret
            return ret

def amount_to_text(number, units_name=u'ريال', cents_name=u'هللة'):
    number = '%.2f' % number
    list = str(number).split('.')
    final_result = (english_number(int(list[0])) or ' ') + ' '+ (units_name or ' ')
    if int(list[1]) >0:
    	final_result +=  u' و ' + (english_number(int(list[1])) or ' ') +'  '+((int(list[1]) != 0) and cents_name or ' ' + u' لا غير ')
    return (final_result+ u' فقط لاغير ').replace('  ',' ')

