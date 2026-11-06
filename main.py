from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.core.window import Window
from kivy.uix.scrollview import ScrollView
from kivy.uix.image import Image
from kivy.config import Config
 
from instructions import txt_instruction, txt_test1, txt_test2, txt_test3, txt_sits
from ruffier import test

from seconds import Seconds
from sits import Sits
from runner import Runner

Window.clearcolor = (.99, .98, .87, 1)
text_color = (.15, .21, .09, 1)
text_secondary_color = (.99, .98, .87, 1)
btn_color = (.37, .42, .21, 1)
btn_secondary_color = (.8, .83, .68, 1)

age = 7
name = ""
p1, p2, p3 = 0, 0, 0
 
def check_int(str_num):
    # возвращает число или False, если строка не конвертируется
    try:
        return int(str_num)
    except:
        return False

class InstrScr(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        header = Image(source='header.png', keep_ratio=True, size_hint_x=1, pos_hint={'x': 0, 'y': 0}, allow_stretch=True)

        main_title = Label(text="Тест Руфье", font_size='34sp', bold=True, size_hint=(1, .3), color=text_color)
        instr = Label(text=txt_instruction, size_hint_y=1, font_size='16sp', color=text_color, valign='top')
 
        input_group = BoxLayout(orientation='vertical', spacing=8)
        self.in_name = TextInput(hint_text='Введите имя', multiline=False, size_hint=(.3, None), height='30sp', pos_hint={'center_x': 0.5})
        self.in_age = TextInput(hint_text='Введите возраст', multiline=False, size_hint=(.3, None), height='30sp', pos_hint={'center_x': 0.5})
        self.btn = Button(text='Начать', size_hint=(0.3, None), pos_hint={'center_x': .5}, color=text_secondary_color, background_color=btn_color)

        input_group.add_widget(self.in_name)
        input_group.add_widget(self.in_age)
        input_group.add_widget(self.btn)

        self.btn.on_press = self.next
 
        # line1 = BoxLayout(size_hint=(0.8, None), height='30sp')
        # line2 = BoxLayout(size_hint=(0.8, None), height='30sp')
        # line1.add_widget(self.in_name)
        # line2.add_widget(self.in_age)
 
        outer = BoxLayout(orientation='vertical', padding=(8, 0, 8, 0))
        outer.add_widget(header)
        outer.add_widget(main_title)
        outer.add_widget(instr)
        outer.add_widget(input_group)
 
        self.add_widget(outer)
 
    def next(self):
        self.btn.color = btn_secondary_color
        name = self.in_name.text
        age = check_int(self.in_age.text)
        if age == False or age < 7:
            age = 7
            self.in_age.text = str(age)
        else:
            self.manager.current = 'pulse1'
 
class PulseScr(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.next_screen = False

        pulse_title = Label(text='Первичное измерение пульса', font_size='34sp', bold=True, size_hint=(1, .3), color=text_color)
        instr = Label(text=txt_test1, color=text_color)

        timer_group = BoxLayout(height='30sp', size_hint=(.4, 1), pos_hint={'center_x': .5})
        self.lbl_sec = Seconds(15, color=text_color, font_size='75sp')
        self.lbl_sec.bind(done=self.sec_finished)
        timer_image = Image(source='hourglass.png', allow_stretch=False, width='10sp')
        timer_group.add_widget(timer_image)
        timer_group.add_widget(self.lbl_sec)

        self.input_group = BoxLayout(orientation='vertical', spacing=8)
        self.in_result = TextInput(hint_text='Введите результат измерений', multiline=False, size_hint=(.3, None), height='30sp', pos_hint={'center_x': 0.5})
        self.in_result.set_disabled(True)
        self.btn = Button(text='Начать', size_hint=(0.3, None), pos_hint={'center_x': .5}, color=text_secondary_color, background_color=btn_color)
        self.btn.on_press = self.next
        self.input_group.add_widget(self.in_result)
        self.input_group.add_widget(self.btn)

        outer = BoxLayout(orientation='vertical', padding=(8, 0, 8, 0), spacing=8)
        outer.add_widget(pulse_title)
        outer.add_widget(instr)
        #outer.add_widget(lbl1)
        outer.add_widget(timer_group)
        outer.add_widget(self.input_group)
    
        self.add_widget(outer)

    def sec_finished(self, *args):
        self.next_screen = True
        self.in_result.set_disabled(False)
        self.btn.set_disabled(False)
        self.btn.text = 'Продолжить'

        self.input_group.remove_widget(self.btn)
        self.btn_back = Button(text='Назад', size_hint=(0.3, None), pos_hint={'center_x': .5}, color=text_secondary_color, background_color=btn_color)
        btn_group = BoxLayout(size_hint=(.6, None), pos_hint={'center_x': .5})
        btn_group.add_widget(self.btn_back)
        btn_group.add_widget(self.btn)
        self.input_group.add_widget(btn_group)
        self.btn_back.on_press = self.back


    def next(self):
        if not self.next_screen:
            self.btn.set_disabled(True)
            self.lbl_sec.start()
        else:
            global p1
            p1 = check_int(self.in_result.text)
            if p1 == False or p1 <= 0:
                p1 = 0
                self.in_result.text = str(p1)
            else:
                self.manager.current = 'sits'
    def back(self):
        self.manager.current = self.manager.previous()


class CheckSits(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.next_screen = False

        left_side = BoxLayout(orientation='vertical', size_hint=(.8, 1), pos_hint={'x': 0})

        sits_title = Label(text='Приседания', font_size='34sp', bold=True, size_hint=(1, .3), color=text_color)
        instr = Label(text=txt_sits, color=text_color)

        timer_group = BoxLayout(height='30sp', size_hint=(.4, 1), pos_hint={'center_x': .5})
        self.lbl_sits = Sits(30, color=text_color, font_size='75sp')
        
        timer_image = Image(source='squat.png', allow_stretch=False, width='10sp')
        timer_group.add_widget(timer_image)
        timer_group.add_widget(self.lbl_sits)

        
        self.btn = Button(text='Начать', size_hint=(0.3, None), pos_hint={'center_x': .5}, color=text_secondary_color, background_color=btn_color)
        self.btn.on_press = self.next

        left_side.add_widget(sits_title)
        left_side.add_widget(instr)
        left_side.add_widget(timer_group)
        left_side.add_widget(self.btn)

        right_side = BoxLayout(size_hint=(.2, 1), pos_hint={'x': 1})

        self.run = Runner(total=30, steptime=1.5, color=text_secondary_color, btn_color=btn_secondary_color, size_hint=(0.4, 1),)
        self.run.bind(finished=self.run_finished)

        right_side.add_widget(self.run)

        outer = BoxLayout(padding=(8, 0, 8, 0), spacing=8)
        outer.add_widget(left_side)
        outer.add_widget(right_side)
    
        self.add_widget(outer)


    def run_finished(self, instance, value):
        self.btn.set_disabled(False)
        self.btn.text = 'Продолжить'
        self.next_screen = True

    def next(self):
        if not self.next_screen:
            self.btn.set_disabled(True)
            self.run.start()
            self.run.bind(value=self.lbl_sits.next)
        else:
            self.manager.current = 'pulse2'


class PulseScr2(Screen):
    def __init__(self, **kwargs):
        self.next_screen = False

        self.stage = 0
        super().__init__(**kwargs)

        header = Image(source='header.png', keep_ratio=True, size_hint_x=1, pos_hint={'x': 0, 'y': 0}, allow_stretch=True)
        title = Label(text='Повторные замеры пульса', font_size='34sp', bold=True, size_hint=(1, .3), color=text_color)
        instr = Label(text=txt_test3, color=text_color)

        timer_group = BoxLayout(size_hint=(.4, None), pos_hint={'center_x': .5}, padding=15)
        self.lbl_sec = Seconds(15, color=text_color, font_size='75sp')
        self.lbl_sec.bind(done=self.sec_finished)
        timer_image = Image(source='hourglass.png', allow_stretch=False, width='10sp')
        timer_group.add_widget(timer_image)
        timer_group.add_widget(self.lbl_sec)

        self.lbl1 = Label(text='Считайте пульс', color=text_color, font_size='16sp', bold=True, size_hint=(1, .5))

        input_group = BoxLayout(orientation='vertical', spacing=8, padding=8)
        self.in_result1 = TextInput(hint_text='Пульс до отдыха', multiline=False, size_hint=(.3, None), height='30sp', pos_hint={'center_x': 0.5})
        self.in_result2 = TextInput(hint_text='Пульс после отдыха', multiline=False, size_hint=(.3, None), height='30sp', pos_hint={'center_x': 0.5})
        self.in_result1.set_disabled(True)
        self.in_result2.set_disabled(True)

        self.btn = Button(text='Начать', size_hint=(0.3, None), pos_hint={'center_x': .5}, color=text_secondary_color, background_color=btn_color)
        self.btn.on_press = self.next

        input_group.add_widget(self.in_result1)
        input_group.add_widget(self.in_result2)
        input_group.add_widget(self.btn)
 
        outer = BoxLayout(orientation='vertical', padding=8, spacing=8)
        outer.add_widget(header)
        outer.add_widget(title)
        outer.add_widget(instr)
        outer.add_widget(self.lbl1)
        outer.add_widget(timer_group)
        outer.add_widget(input_group)
 
        self.add_widget(outer)

    def sec_finished(self, *args):
     if self.lbl_sec.done == True:
       if self.stage == 0:
          # закончили первый подсчет, отдыхаем
          self.stage = 1
          self.lbl1.text = 'Отдыхайте'
          self.lbl_sec.restart(30)
          self.in_result1.set_disabled(False)
       elif self.stage == 1:
          # закончили отдых, считаем
          self.stage = 2
          self.lbl1.text='Считайте пульс'
          self.lbl_sec.restart(15)
       elif self.stage == 2:
          self.in_result2.set_disabled(False)
          self.btn.set_disabled(False)
          self.btn.text = 'Завершить'
          self.next_screen = True
 
    def next(self):
        if not self.next_screen:
            self.btn.set_disabled(True)
            self.lbl_sec.start()
        else:
            global p2, p3
            p2 = check_int(self.in_result1.text)
            p3 = check_int(self.in_result2.text)
            if p2 == False:
                p2 = 0
                self.in_result1.text = str(p2)
            elif p3 == False:
                p3 = 0
                self.in_result2.text = str(p3)
            else:
                # переходим 
                self.manager.current = 'result'
 
class Result(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
 
        self.outer = BoxLayout(orientation='vertical', padding=0, spacing=8)
        title = Label(text='Результаты', font_size='34sp', bold=True, size_hint=(1, .3), color=text_color)
        self.instr = Label(text = '', color=text_color, markup=True)
        self.outer.add_widget(title)
        self.outer.add_widget(self.instr)
 
        self.add_widget(self.outer)
        self.on_enter = self.before
  
    def before(self):
        global name
        result = test(p1, p2, p3, age)
        self.instr.text = name + '\n' + result[0]
        image = Image(source=f'{result[1]}.png', allow_stretch=False, width='20sp')
        self.outer.add_widget(image)


 
class HeartCheck(App):
   def build(self):
       sm = ScreenManager()
       sm.add_widget(InstrScr(name='instr'))
       sm.add_widget(PulseScr(name='pulse1'))
       sm.add_widget(CheckSits(name='sits'))
       sm.add_widget(PulseScr2(name='pulse2'))
       sm.add_widget(Result(name='result'))
       return sm
 
app = HeartCheck()
app.run()
