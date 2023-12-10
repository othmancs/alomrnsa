# -*- coding: utf-8 -*-


to_9=(
'', '', '', u'ثلاث', u'أربع', u'خمس', u'ست', u'سبع', u'ثماني', u'تسع')
to_19 = (
u'صفر', u'واحد', u'اثنان', u'ثلاثة', u'أربعة', u'خمسة', u'ستة', u'سبعة', u'ثمانية', u'تسعة', u'عشرة', u'أحد عشر', u'اثنا عشر',
u'ثلاثة عشر' ,
u'أربعة عشر', u'خمسة عشر', u'ستة عشر', u'سبعة عشر', u'ثمانية عشر', u'تسعة عشر')

tens = (u'عشرون', u'ثلاثون', u'أربعون', u'خمسون', u'ستون', u'سبعون', u'ثمانون', u'تسعون')
denom = ('',
         u'ألف', u'مليون', u'مليار', u'تريليون', u'كوادريليون')


def _convert_nn(val):
    """convert a value < 100 to English.
    """
    if val < 20:
        return to_19[val]
    for (dcap, dval) in ((k, 20 + (10 * v)) for (v, k) in enumerate(tens)):
        if dval + 10 > val:
            if val % 10:
                return to_19[val % 10]+ u' و ' +dcap
            return dcap


def _convert_nnn(val):
    """
        convert a value < 1000 to english, special cased because it is the level that kicks
        off the < 100 special case.  The rest are more general.  This also allows you to
        get strings in the form of 'forty-five hundred' if called directly.
    """
    word = u''
    (mod, rem) = (val % 100, val // 100)
    if rem < 3 and rem >0:
        word=u'مائة' if rem ==1 else u'مائتين'
    elif rem<10 and rem > 2:
        word=to_9[rem]+ u'مائة'
        if mod > 0:
            word += ' '

    if rem >9:
        word = to_19[rem] + u' مائة'
        if mod > 0:
            word += ' '
    if mod > 0:
        word += ' '
        word += u'و'+' '+_convert_nn(mod)
    return word


def english_number(val):
    if val < 100:
        return _convert_nn(val)
    if val < 1000:
        return _convert_nnn(val)
    for (didx, dval) in ((v - 1, 1000 ** v) for v in range(len(denom))):
        if dval > val:
            mod = 1000 ** didx
            l = val // mod
            r = val - (l * mod)
            if l<100:
                ret = _convert_nn(l) + ' ' + denom[didx]
            else:
                ret = _convert_nnn(l) + ' ' + denom[didx]
            if r > 0:
                ret = ret + u' و ' + english_number(r)
            return ret
def _get_currency_name_by_code(cur):
    result={'SDG':['جنيه','قروش','قرش'],
            'AED':['درهم','فلسات','فلس'],
            'CFA':['فرنك','سنتات','سنت'],
            'EGP':['جنيه','قروش','قرش'],
            'EUR':['يورو','سنتات','سنت'],
            'USD':['دولار','سنتات','سنت'],
            'SSP':['جنيه','قروش','قرش'],
            'SAR':['ريال','هللات','هللة']
            }
    return result[cur.upper()]


def amount_to_text_arabic(number, currency):
    number = '%.2f' % number
    units_name = currency
    list = str(number).split('.')
    start_word = english_number(int(list[0]))
    end_word = english_number(int(list[1]))
    cents_number = int(list[1])
    cents_name = (cents_number > 10 or cents_number==0) and _get_currency_name_by_code(currency)[2]  or _get_currency_name_by_code(currency)[1]
    #
    # return ' '.join(filter(None,
    #                        [start_word, units_name,  'و'.decode('utf-8'),
    #                         end_word, cents_name]))
    return u'فقط '+start_word+' '+_get_currency_name_by_code(currency)[0]+' '+u'و'+' '+end_word+" "+cents_name