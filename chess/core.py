import random
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont


class chessboard:
    def __init__(self, width, height, lines, line_width=14, line_color="black", bg_color=(178, 137, 115)):
        self.width = width
        self.height = height
        self.lines = lines
        self.line_width = line_width
        self.line_color = line_color
        self.image = Image.new("RGB", (width, height), color=bg_color)
        self.pen = ImageDraw.Draw(self.image)
        self._cal = self.width / self.lines
        self._text_size = self._cal - self._cal / 1.8
        self.font = ImageFont.truetype("chess/lucon.ttf", size=int(self._text_size))
        self.draw_chessboard()

    def draw_chessboard(self):
        self.draw_width()
        self.draw_height()

    def draw_text(self, width, height, text):
        self.pen.text((width, height), text, fill=self.line_color, font=self.font)

    def draw_point(self, xy, color):
        #x, y = (self._cal*d+(self.line_width/2) for d in xy)  #
        x, y = ((self._cal * d+(self.line_width/2))+self._cal/2 for d in xy)
        q = self._cal-self.line_width
        self.pen.ellipse((x, y, x+q, y+q), fill=color)

    def draw_width(self):
        offset = 0
        for c in range(self.lines):
            c += 1
            if c == self.lines:
                break
            self.draw_text(0, self._cal * c+1 - (self.line_width * 2), str(c-1))
            #self.pen.line((offset, self._cal * c + offset, self.width, self._cal * c + offset), fill=self.line_color, width=self.line_width)
            self.pen.line((self._text_size, self._cal * c + offset, self.width, self._cal * c + offset), fill=self.line_color,
                          width=self.line_width)

    def draw_height(self):
        offset = 0
        for c in range(self.lines):
            c += 1
            if c == self.lines:
                break
            self.draw_text(self._cal * c + 1 - (self.line_width * 2), 0, str(c - 1))
            #self.pen.line((self._cal * c + offset, offset, self._cal * c + offset, self.height), fill=self.line_color, width=self.line_width)
            self.pen.line((self._cal * c + offset, self._text_size, self._cal * c + offset, self.height), fill=self.line_color,
                          width=self.line_width)

    def show(self):
        self.image.show()

    def out(self, **kwargs):
        res = BytesIO()
        self.image.save(res, "JPEG", **kwargs)
        return res.getvalue()


class ChessControl:
    def __init__(self, size=12):
        self.map = []
        self.size = size
        self.render = chessboard(800, 800, size, line_width=6)
        for _ in range(size):
            buf = []
            for _ in range(size):
                buf.append(0)
            self.map.append(buf)

    def get_status(self, x, y, team):
        count = 1
        for i in range(5):  # 左上
            i += 1
            if count == 5:
                return True
            if x - i >= 0 and y - i >= 0:
                try:
                    if self.map[y-i][x-i] == team:
                        count += 1
                    else:
                        break
                except IndexError:
                    break
            else:
                break
        for i in range(5):  # 右下
            i += 1
            if count == 5:
                return True
            if x + i >= 0 and y + i >= 0:
                try:
                    if self.map[y+i][x+i] == team:
                        count += 1
                    else:
                        break
                except IndexError:
                    break
            else:
                break
        count = 1
        for i in range(5):  # 右上
            i += 1
            if count == 5:
                return True
            if x + i >= 0 and y - i >= 0:
                try:
                    if self.map[y-i][x+i] == team:
                        count += 1
                    else:
                        break
                except IndexError:
                    break
            else:
                break
        for i in range(5):  # 左下
            i += 1
            if count == 5:
                return True
            if x - i >= 0 and y + i >= 0:
                try:
                    if self.map[y+i][x-i] == team:
                        count += 1
                    else:
                        break
                except IndexError:
                    break
            else:
                break
        count = 1
        for i in range(5):  # 左
            i += 1
            if count == 5:
                return True
            if x - i >= 0:
                try:
                    if self.map[y][x-i] == team:
                        count += 1
                    else:
                        break
                except IndexError:
                    break
            else:
                break
        for i in range(5):  # 右
            i += 1
            if count == 5:
                return True
            if x + i >= 0:
                try:
                    if self.map[y][x+i] == team:
                        count += 1
                    else:
                        break
                except IndexError:
                    break
            else:
                break
        count = 1
        for i in range(5):  # 上
            i += 1
            if count == 5:
                return True
            if y - i >= 0:
                try:
                    if self.map[y-i][x] == team:
                        count += 1
                    else:
                        break
                except IndexError:
                    break
            else:
                break
        for i in range(5):  # 下
            i += 1
            if count == 5:
                return True
            if y + i >= 0:
                try:
                    if self.map[y+i][x] == team:
                        count += 1
                    else:
                        break
                except IndexError:
                    break
            else:
                break

    def put(self, x, y, team):
        if -1 < x <= self.size-2 and -1 < y <= self.size-2:  # 防止越界
            if self.map[y][x] == 0:
                self.map[y][x] = team
                if team == -1:
                    self.render.draw_point((x, y), "black")
                else:
                    self.render.draw_point((x, y), "white")
                if self.get_status(x, y, team):
                    return 1
                else:
                    return 0
            else:
                return -1
        else:
            return -2

    def get_image(self, **kwargs):
        return self.render.out(**kwargs)

    def __hash__(self):
        return str(random.random())

if __name__ == '__main__':
    x = ChessControl(14)
    x.put(0, 0, -1)
    x.put(1, 1, -1)
    x.put(10, 10, 1)
    x.put(12, 13, 1)
    x.render.show()