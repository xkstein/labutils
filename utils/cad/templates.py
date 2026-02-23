import gdspy
import numpy as np

def chip_template(rows, columns, ebeamfield, block_shift_x, block_shift_y, layers, etch_facet, label, heaters, **kwargs):
    objects = []
    # make e beam fields
    field = gdspy.Rectangle((0,0), (ebeamfield, ebeamfield), layer=layers['ROI'])
    for row in range(rows):
        for column in range(columns):
            # for each row/column add field
            # blockspace_y adds 200 um extra spacing between chips
            new_field = gdspy.copy(field, column * block_shift_x, row * block_shift_y + etch_facet);
            objects.append(new_field);

    # make facets (space between chips)
    facet = gdspy.Rectangle((0, 0), (block_shift_x * columns, -(block_shift_y-ebeamfield)) ,layer=layers["DRIE"]);
    for row in range(rows + 1):
        new_facet = gdspy.copy(facet, 0, row * block_shift_y + etch_facet)
        objects.append(new_facet)

    # add labels
    if 'bottom' in label:
        x_center = (columns - 1) * block_shift_x + ebeamfield / 2
        y_center = ebeamfield / 2 + etch_facet
        arrow_width = 100
        arrow_ratio = np.sqrt(3)
        arrow = [(x_center - arrow_width / 2, y_center), (x_center - arrow_width, y_center), (x_center, y_center + arrow_ratio * arrow_width), (x_center + arrow_width, y_center), (x_center + arrow_width / 2, y_center), (x_center + arrow_width / 2, y_center - arrow_ratio * arrow_width), (x_center - arrow_width / 2, y_center - arrow_ratio * arrow_width)]
        label_bottom = gdspy.Polygon(arrow, layer=layers['Metal'])
#        label_bottom = gdspy.Text(label['bottom'], size=600, 
#               position=((columns - 1) * block_shift_x + 300, (ebeamfield - 466.7) / 2 + etch_facet - 133.33), layer=label['layer'])
        for row in range(rows):
            label_new = gdspy.copy(label_bottom, 0, row * (ebeamfield + etch_facet))
            objects.append(label_new)

    if 'top' in label:
        for ind, row in enumerate(range(rows)):
            label_top = gdspy.Text(label['top'] + f'{ind}', size=600, position=(ebeamfield - 150, block_shift_y * ind + (ebeamfield - 866.67) / 2 + etch_facet), layer=label['layer'], angle=np.pi / 2)
            objects.append(label_top)

    if 'subtitle' in label:
        subtitle = gdspy.Text(label['subtitle'], size=20, position=(ebeamfield - 200, (ebeamfield - 866.67) / 2 + etch_facet), layer=label['layer'], angle=np.pi / 2)
        for row in range(rows):
            subtitle_new = gdspy.copy(subtitle, 0, row * (ebeamfield + etch_facet) )
            objects.append(subtitle_new)

    if heaters:
        pad = gdspy.Rectangle((-heaters['pad_size']/2,-heaters['pad_size']/2),(heaters['pad_size']/2,heaters['pad_size']/2),layer=layers['Metal']);
        pad.fillet(30)

        pads = []
        for i in [100, 300, 500, 700, 900]:
            pads.append(
                    gdspy.copy(pad, 100, i + etch_facet)
            )

        for row in range(rows):
            for col in range(1, columns - 1):
                if heaters['make_pads_default']:
                    if [col, row] in heaters['skip_pads']:
                        continue
                else:
                    if [col, row] not in heaters['make_pads']:
                        continue
                new_pads = [ gdspy.copy(pad, col * block_shift_x, row * block_shift_y) for pad in pads ]
                objects += new_pads

    return objects

def heater_pads(start_x, start_y, pad_size, pos_y=[100,300,500,700,900], layer=0):
    pad = gdspy.Rectangle((-pad_size/2,-pad_size/2),(pad_size/2,pad_size/2), layer=layer)
    pad.fillet(30)

    pads = []
    for i in pos_y:
        pads.append(
                gdspy.copy(pad, start_x, i + start_y)
        )
    return pads
