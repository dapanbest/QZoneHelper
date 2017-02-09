# coding = utf-8
from selenium import webdriver
import selenium.common.exceptions
import datetime
import time
import os
import PraiseTool
import Stylesheet


mfile_path = None
driver = None
mfile = None
is_finished = None
first_time = None
praise = PraiseTool.PraiseTool()


def get_dynamic_info(this_dynamic):
    try:
        global first_time, is_finished
        user_name = this_dynamic.find_element_by_class_name('username').text
        send_time = this_dynamic.find_element_by_class_name('time').text
        content = this_dynamic.find_element_by_class_name('feed-bd').find_element_by_class_name('txt').text
        if first_time is None:
            first_time = send_time
        if not PraiseTool.compare_time(send_time, praise.params['oldest']):
            praise.params['oldest'] = first_time
            is_finished = True
            return False
        if content is None or content == '':
            content = '[发了一堆图片]'
        if praise.is_auto_clip(user_name):
            driver.execute_script("arguments[0].scrollIntoView();", this_dynamic)
            time.sleep(1)
            this_dynamic.screenshot('Screenshots/' + user_name + '@'
                                    + datetime.datetime.now().strftime('%H-%M-%S') + '.jpg')
            time.sleep(1)
        if praise.is_auto_like(user_name):
            like_btn = this_dynamic.find_element_by_class_name('item js-like like')
            if like_btn.text == '赞':
                driver.execute_script("arguments[0].scrollIntoView();", like_btn)
                mfile.write('<h4>' + user_name + '在' + send_time + '发表说说(已赞)：</h4><p>' + content + '</p>')
                time.sleep(1)
                like_btn.click()
                time.sleep(1)
            else:
                mfile.write('<h4>' + user_name + '在' + send_time + '发表说说(之前赞过)：</h4><p>' + content + '</p>')
        else:
            mfile.write('<h4>' + user_name + '在' + send_time + '发表说说：</h4><p>' + content + '</p>')
        comments = this_dynamic.find_elements_by_class_name('comment-item')
        for comment in comments:
            comment_user = comment.find_element_by_class_name('username').text
            comment_content = comment.find_element_by_class_name('comment-text').text
            if comment_content is None or comment_content == '':
                continue
            mfile.write('<small class="name">' + comment_user + '：' + comment_content + '</small><br>')
            try:
                reply_items = comment.find_element_by_class_name('reply-list').find_elements_by_class_name('item')
                for reply_item in reply_items:
                    reply_users = reply_item.find_elements_by_class_name('username')
                    reply_from = reply_users[0].text
                    reply_to = reply_users[1].text
                    reply_text = reply_item.find_element_by_class_name('reply-txt').text
                    if reply_text is None or reply_text == '':
                        continue
                    mfile.write('<small class="name">' + reply_from + '回复' + reply_to + '：'
                                + reply_text + '</small><br>')
            except selenium.common.exceptions.NoSuchElementException:
                continue
        mfile.write('<hr>')
        return True
    except selenium.common.exceptions.NoSuchElementException:
        pass


def main():
    global mfile_path, driver, mfile, praise, is_finished, first_time, is_finished
    mfile_path = 'DynamicLog/' + datetime.datetime.now().strftime('%m-%d-%H-%M-%S') + '.html'
    driver = webdriver.Edge(executable_path="WebDriver.exe")
    mfile = open(mfile_path, 'w', encoding='utf-8')
    driver.set_window_size(540, 1440)
    driver.get('https://h5.qzone.qq.com/mqzone/index')
    mfile.write(Stylesheet.stylesheet)
    is_finished = False
    try:
        driver.implicitly_wait(5000)
        login_panel = driver.find_element_by_id('web_login')
        user_name_box = login_panel.find_element_by_id('g_u').find_element_by_name('u')
        user_password_box = login_panel.find_element_by_id('g_p').find_element_by_name('p')
        user_name_box.clear()
        user_password_box.clear()
        user_name_box.send_keys(praise.params['account'])
        user_password_box.send_keys(praise.params['password'])
        login_panel.find_element_by_id('go').click()
        time.sleep(3)
        dynamic_count = 0
        driver.implicitly_wait(0)
        dynamics = driver.find_elements_by_class_name('feed dataItem')
        while not is_finished:
            for dynamic in dynamics:
                if is_finished:
                    break
                elif get_dynamic_info(dynamic):
                    dynamic_count += 1
            driver.find_element_by_class_name('btn js_morebtn').click()
            time.sleep(2)
            dynamics = driver.find_elements_by_class_name('feed dataItem')[len(dynamics):]
        mfile.write('<b>抓取结束，共获得' + str(dynamic_count) + '条说说</b></div></body></html>')
        mfile.close()
        if dynamic_count == 0:
            os.remove(mfile_path)
        driver.close()
        driver.quit()
        praise.save_params()
    except selenium.common.exceptions.NoSuchElementException:
        mfile.close()
        os.remove(mfile_path)
        exit(1)

time_tick = 10
# noinspection PyBroadException
try:
    time_tick = praise.params.get('timetick', 10)
    time_tick = int(time_tick)
except:
    time_tick = 2
finally:
    if time_tick < 1:
        time_tick = 10
    while True:
        main()
        time.sleep(60 * time_tick)