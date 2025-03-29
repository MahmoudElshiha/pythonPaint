while (2 * ry2 * x) <= (2 * rx2 * y):
            points.extend([
                QPoint(xc + x, yc + y),
                QPoint(xc - x, yc + y),
                QPoint(xc + x, yc - y),
                QPoint(xc - x, yc - y)
            ])
            x += 1
            if p1 < 0:
                p1 += 2 * ry2 * x + ry2
            else:
                y -= 1
                p1 += 2 * ry2 * x - 2 * rx2 * y + ry2

        # Region 2
        p2 = (ry2 * (x + 0.5) ** 2) + (rx2 * (y - 1) ** 2) - (rx2 * ry2)
        while y >= 0:
            points.extend([
                QPoint(xc + x, yc + y),
                QPoint(xc - x, yc + y),
                QPoint(xc + x, yc - y),
                QPoint(xc - x, yc - y)
            ])
            y -= 1
            if p2 > 0:
                p2 -= 2 * rx2 * y + rx2
            else:
                x += 1
                p2 += 2 * ry2 * x - 2 * rx2 * y + rx2
        return points