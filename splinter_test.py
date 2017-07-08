from splinter import Browser
browser = Browser()

browser.visit('http://google.com')

browser.fill('q', 'splinter - python acceptance testing for web applications')




button = browser.find_by_name('btnG')

button.click()


print(browser.html)

browser.quit()
