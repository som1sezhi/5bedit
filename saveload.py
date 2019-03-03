def save(lvl):
    f = open('lvl.txt', 'w+')
    lvl_w = len(lvl)
    lvl_h = len(lvl[0])
    hmode = False
    for col in lvl:
        for cell in col:
            if len(cell) > 1:
                hmode = True
                break
    
    f.write('untitled\n')
    f.write('%d,%d,00,00,%s\n' % (lvl_w, lvl_h, 'H' if hmode else 'L'))
    
    for y in range(lvl_h):
        row = ''
        for x in range(lvl_w):
            cell = lvl[x][y]
            if hmode:
                if len(cell) == 1:
                    row += ('.' + cell)
                else:
                    row += cell
            else:
                row += cell

        f.write(row + '\n')

    f.write('00\n')
    f.write('000000')
    f.close()
