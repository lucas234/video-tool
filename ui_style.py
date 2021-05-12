# @Time    : 2021/3/25 10:46
# @Author  : lucas
# @File    : style.py
# @Project : pyqt
# @Software: PyCharm

font_size = 14
font_color = "#4d7d57"
font_family = "verdana"
header_style = f'''QHeaderView::section{{
                     border-top: 1px solid #D8D8D8;
                     border-left: 1px solid #D8D8D8;
                     border-right: 1px solid #D8D8D8;
                     border-bottom: 1px solid #D8D8D8;
                     padding:4px;
                     color:{font_color};font-size:{font_size}px;
                     font-weight:bold;font-family:{font_family};
                    }}'''
# background-color:#f3f8f3;
table_data_style = f"color:#658d56;font-size:12px;font-weight:bold;font-family:{font_family};"
search_input_style = f'''border-radius:6px;color:{font_color};font-size:{font_size}px;
                         font-weight:bold;font-family:{font_family};'''
search_button_style = f'''QPushButton:hover{{background-color:#abdaff;}}
                          QPushButton{{padding:2px 2px;border:1px solid;
                          border-color:gray; 
                          border-radius:6px;color:{font_color};font-size:{font_size}px;
                          font-weight:bold;font-family:{font_family};}}'''
menu_style = f'color:#406863;font-size:12px;font-weight:bold;font-family:{font_family};'
label_style = f"color:{font_color};font-size:{font_size}px;font-weight:bold;font-family:{font_family};"
download_list_tab = f'''
                     QTabWidget::pane {{border: 1px solid black;background: white;}}
                     QTabBar::tab:selected {{background-color: #52c2fe;margin-top: 2px;}}
                     QTabBar::tab{{height:30px; width:108px; color:{font_color};font: {font_size}px}}
                    '''

# player
play_input_style = f'''color:{font_color};font-size:{font_size}px;
                       font-family:{font_family};
                       border-style: solid;
                       border-width: 1px;
                       border-radius: 5px;
                       border-color: gray;
                       padding:1px 1px;
                    '''
play_btn_style = '''QPushButton{ border-image:url(assets/player.png);
                                 border-radius:4px;
                                 padding: 2px 2px;
                                 border: 2px;
                                 margin-bottom: 2px;
                                 }'''
# background-color:#fffcff;

download_btn_style = '''QPushButton{ border-image:url(assets/play-download.png);
                                 border-radius:4px;
                                 padding: 2px 2px;
                                 border: 2px;
                                 margin-bottom: 2px;
                                 }'''
# background-color:#f1fffb;

download_header_style = f'''QHeaderView::section{{
                     border-top: 1px solid #D8D8D8;
                     border-left: 1px solid #D8D8D8;
                     border-right: 1px solid #D8D8D8;
                     border-bottom: 1px solid #D8D8D8;
                     padding:4px;
                     color:{font_color};font-size:12px;
                     font-weight:bold;font-family:{font_family};
                    }}'''

combobox_style = '''
                    QComboBox {
                          border: 1px solid gray;
                          border-radius: 3px;
                          padding: 1px 18px 1px 3px;
                          min-width: 6em;
                        }
                    QComboBox:on { /* shift the text when the popup opens */
                      padding-top: 3px;
                      padding-left: 4px;
                     }
                    QComboBox::drop-down {
                      subcontrol-origin: padding;
                      subcontrol-position: top right;
                      width: 15px;
                      border-left-width: 1px;
                      border-left-color: darkgray;
                      border-left-style: solid; /* just a single line */
                      border-top-right-radius: 3px; /* same radius as the QComboBox */
                      border-bottom-right-radius: 3px;
                     }
                    QComboBox::down-arrow {
                      image: url(assets/down.png);
                     }
                    QComboBox::down-arrow:on { /* shift the arrow when popup is open */
                      image: url(assets/right.png);
                      top: 1px;
                      left: 1px;
                     }
                    '''

# settings
btn_open_style = '''QPushButton{ border-image:url(assets/file.png);
                                 border-radius:4px;
                                 padding: 2px 2px;
                                 border: 2px;
                                 margin-bottom: 2px;
                                 }'''
# background-color:#fffcff;
setting_input_style = f'''QLineEdit{{ color:gray;font-size:{font_size}px;
                                      font-family:{font_family};border-style: solid;
                                      border-width: 1.3px;border-radius: 3px;
                                      border-color: gray;padding: 1px 1px;}}
                          QLineEdit::hover{{border-color: #00b372;border-width: 2px;}}
                        '''

spin_box_style = f'''QSpinBox{{ color:gray;font-size:{font_size}px;
                                max-width: 80;height: 18;
                                font-family:{font_family};
                                border-width: 1.3px;
                                border-color: gray;padding: 1px 1px;}}
                          QSpinBox::hover{{border-color: #00b372;border-width: 1.5px;}}
                        '''
checkbox_style = "padding: 8px 2px;"


