""" 
@author: lileilei
@file: view.py 
@time: 2018/1/31 13:20 
"""
from  flask import  redirect,request,render_template,session,url_for,flash,jsonify,Blueprint
from  app.models import *
from app.form import  *
import os,time,datetime
from app.common.pares_excel_inter import pasre_inter
from app.common.py_Html import createHtml
from app.common.requ_case import Api
from app.common.panduan import assert_in
from app.test_case.Test_case import ApiTestCase
from app.common.send_email import send_emails
from flask.views import View
from flask_login import current_user,login_required
from app.common.Dingtalk import send_ding
case = Blueprint('case', __name__)
def get_pro_mo():
    projects=Project.query.all()
    model=Model.query.all()
    return  projects,model
class AddtestcaseView(View):
    methods=['GET','POST']
    @login_required
    def dispatch_request(self):
        form=Interface_yong_Form()
        project, models = get_pro_mo()
        if current_user.is_sper == True:
            projects=Project.query.filter_by(status=False).order_by('-id').all()
        else:
            projects=[]
            id=[]
            for i in current_user.quanxians:
                if  (i.projects in id)==False:
                    if i.projects.status == False:
                        projects.append(i.projects)
                        id.append(i.projects)
        if request.method=='POST' and form.validate_on_submit :
            save=request.form.get('save')
            yongli_nam=request.form.get('project')
            mode=request.form.get('model')
            interface_name=request.form.get('interface_name')
            interface_url=request.form.get('interface_url')
            interface_header=request.form.get('interface_headers')
            interface_meth=request.form.get('interface_meth')
            interface_can=request.form.get('interface_can')
            interface_re=request.form.get('interface_rest')
            yilai_data=request.values.get("yilaicanshu")
            yilai_test= request.values.get("jiekou")
            if yilai_test is None or yilai_test == '请选择依赖接口':
                yilai_dat=None
                yilai_tes=None
            else:
                yilai_tes=yilai_test
                if yilai_data is None or yilai_data=='':
                    flash(u'选择依赖后必须填写获取依赖的接口的字段')
                    return render_template('add/add_test_case.html', form=form, projects=projects, models=models)
                yilai_dat=yilai_data
            if yongli_nam is None or mode is None or interface_name=='' or interface_header==''or interface_url=='' or interface_meth=='' or interface_re=='':
                flash(u'请准确填写用例')
                return render_template('add/add_test_case.html', form=form, projects=projects, models=models)
            project_id = Project.query.filter_by(project_name=yongli_nam).first().id
            models_id = Model.query.filter_by(model_name=mode).first().id
            if save==1 or save=='1':
                saves=False
            elif save==2 or save=='2':
                saves=True
            else:
                flash(u'选择保存测试结果出现异常')
                return render_template('add/add_test_case.html', form=form, projects=projects, models=models)
            try:
                newcase=InterfaceTest(projects_id=project_id,model_id=models_id,Interface_name=interface_name,
                                      Interface_headers=interface_header,Interface_url=interface_url,Interface_meth=interface_meth,
                                      Interface_pase=interface_can,Interface_assert=interface_re,
                                      Interface_user_id=current_user.id,saveresult=saves,pid=(yilai_tes),getattr_p=yilai_dat)
                db.session.add(newcase)
                db.session.commit()
                flash(u'添加用例成功')
                return redirect(url_for('home.yongli'))
            except Exception as e:
                db.session.rollback()
                flash(u'添加用例失败')
                return redirect(url_for('home.yongli'))
        return render_template('add/add_test_case.html', form=form, projects=projects, models=models)
class Deletecase(View):
    methods=['GET','POST']
    @login_required
    def dispatch_request(self,id):
        next=request.headers.get('Referer')
        testcase=InterfaceTest.query.filter_by(id=id).first()
        testcase.status=True
        db.session.commit()
        flash(u'删除成功')
        return redirect(next or url_for('home.yongli'))
class EditcaseView(View):
    methods=['GET','POST']
    @login_required
    def dispatch_request(self,id):
        next = request.headers.get('Referer')
        project, models = get_pro_mo()
        if current_user.is_sper == True:
            projects=Project.query.filter_by(status=False).order_by('-id').all()
        else:
            projects=[]
            id=[]
            for i in current_user.quanxians:
                if  (i.projects in id)==False:
                    if i.projects.status == False:
                        projects.append(i.projects)
                        id.append(i.projects)
        edit_case=InterfaceTest.query.filter_by(id=id).first()
        if request.method=='POST':
            save = request.form.get('save')
            yongli_nam = request.form.get('project')
            mode = request.form.get('model')
            url=request.form.get('url')
            meth=request.form.get('meth')
            headers=request.form.get('headers')
            parme=request.form.get('parme')
            reque=request.form.get('reque')
            yilai_data = request.values.get("yilaicanshu")
            yilai_test = request.values.get("jiekou")
            if yilai_test is None or yilai_test == '请选择依赖接口':
                yilai_dat = None
                yilai_tes = None
            else:
                yilai_tes = yilai_test
                if yilai_data is None or yilai_data == '':
                    flash(u'选择依赖后必须填写获取依赖的接口的字段')
                    return render_template('edit/edit_case.html', edit=edit_case, projects=projects, models=models)
                yilai_dat = yilai_data
            if yongli_nam ==None  or mode== None or url==''or headers=='' or meth==''  or reque=='':
                flash(u'请确定各项参数都正常填写')
                return render_template('edit/edit_case.html', edit=edit_case, projects=projects, models=models)
            projects_id = Project.query.filter_by(project_name=yongli_nam).first().id
            model_id = Model.query.filter_by(model_name=mode).first().id
            if  save is None:
                saves = False
            elif  save =='是':
                saves = True
            else:
                flash(u'选择保存测试结果出现异常')
                return render_template('edit/edit_case.html', edit=edit_case, projects=projects, models=models)
            edit_case.projects_id=projects_id
            edit_case.model_id=model_id
            edit_case.Interface_url=url
            edit_case.Interface_headers=headers
            edit_case.Interface_meth=meth
            edit_case.Interface_pase=parme
            edit_case.Interface_assert=reque
            edit_case.Interface_user_id=current_user.id
            edit_case.saveresult=saves
            edit_case.pid=yilai_tes
            edit_case.getattr_p=yilai_dat
            try:
                db.session.commit()
                flash(u'编辑成功')
                return redirect( url_for('home.yongli'))
            except:
                db.session.rollback()
                flash(u'编辑失败，请重新编辑！')
                return render_template('edit/edit_case.html', edit=edit_case, projects=projects, models=models)
        return render_template('edit/edit_case.html', edit=edit_case, projects=projects, models=models)
class SeryongliView(View):
    methods=['GET','POST']
    @login_required
    def dispatch_request(self):
        models=Model.query.all()
        if current_user.is_sper == True:
            projects=Project.query.filter_by(status=False).order_by('-id').all()
        else:
            projects=[]
            id=[]
            for i in current_user.quanxians:
                if  (i.projects in id)==False:
                    if i.projects.status == False:
                        projects.append(i.projects)
                        id.append(i.projects)
        if request.method=='POST':
            projecct=request.form.get('project')
            model=request.form.get('model')
            if projecct =='':
                interd=InterfaceTest.query.filter(InterfaceTest.model_id==int(model)).all()
                return render_template('home/ser_yonglo.html', yonglis=interd, projects=projects, models=models)
            if model =='':
                interd=InterfaceTest.query.filter(InterfaceTest.projects_id==int(projecct)).all()
                return render_template('home/ser_yonglo.html', yonglis=interd, projects=projects, models=models)
            interd=InterfaceTest.query.filter(InterfaceTest.projects_id==int(projecct),InterfaceTest.model_id==int(model)).order_by('-id').all()
            return render_template('home/ser_yonglo.html', yonglis=interd, projects=projects, models=models)
        return redirect(url_for('home.yongli'))
class DaorucaseView(View):
    methods=['GET','POST']
    @login_required
    def dispatch_request(self):
        if request.method == 'POST':
            file = request.files['myfile']
            if file and '.' in file.filename and file.filename.split('.')[1]=='xlsx':
                filename='jiekoucase.xlsx'
                file.save(filename)
                jiekou_bianhao,interface_name,project_nam, model_nam, interface_url,interfac_header, interface_meth, interface_par, interface_bas = pasre_inter(filename)
                try:
                    for i in range(len(jiekou_bianhao)):
                        projects_id = Project.query.filter_by(project_name=project_nam[i]).first().id
                        model_id = Model.query.filter_by(model_name=model_nam[i]).first().id
                        new_interface = InterfaceTest(projects_id=projects_id, model_id=model_id,Interface_name=str(interface_name[i]), Interface_url=str(interface_url[i]),Interface_headers=interfac_header[i],Interface_meth=str(interface_meth[i]), Interface_pase=(interface_par[i]),Interface_assert=str(interface_bas[i]),Interface_user_id=User.query.filter_by(username=session.get('username')).first().id)
                        db.session.add(new_interface)
                    db.session.commit()
                    flash(u'导入成功')
                    return redirect(url_for('home.yongli'))
                except:
                    db.session.rollback()
                    flash(u'导入失败，请检查格式是否正确')
                    return render_template('daoru_case.html')
            flash(u'导入失败')
            return render_template('daoru_case.html')
        return  render_template('daoru_case.html')
class MakeonecaseView(View):#这里为不需要测试环境区分的，
    methods=['GET','POST']
    @login_required
    def dispatch_request(self,id):
        next=request.headers.get('Referer')
        case=InterfaceTest.query.filter_by(id=id).first()
        if case.pid != None:
            tesyi = InterfaceTest.query.filter_by(id=int(case.pid)).first()
            testres = TestcaseResult.query.filter_by(case_id=tesyi.id).first()
            if testres is None:
                case.Interface_is_tiaoshi = True
                case.Interface_tiaoshi_shifou = True
                db.session.commit()
                flash(u'失败，请查看依赖用例是否测试')
                return redirect(next or url_for('home.yongli'))
            huoquyilai = testres.result
            canshu = case.getattr_p
            try:
                yilaidata = eval(huoquyilai)[canshu]
            except Exception as e:
                case.Interface_is_tiaoshi = True
                case.Interface_tiaoshi_shifou = True
                db.session.commit()
                flash(u'测试用例获取依赖数据失败')
                return redirect(next or url_for('home.yongli'))
        try:
            pasrms = eval(case.Interface_pase)
            pasrms.update({canshu: yilaidata})
        except:
            return jsonify({'code': 152, 'msg': '测试参数应该是字典格式！'})
        me=Api(url=case.Interface_url,fangshi=case.Interface_meth,params=pasrms,headers=case.Interface_headers)
        result=me.testapi()
        retur_re=assert_in(case.Interface_assert,result)
        try:
            if retur_re=='pass':
                case.Interface_is_tiaoshi = True
                case.Interface_tiaoshi_shifou = False
                if case.saveresult is True:
                    new_testre=TestcaseResult(case_id=case.id)
                    new_testre.result=str(result)
                    db.session.add(new_testre)
                db.session.commit()
                flash(u'用例测试通过')
                return redirect(next or url_for('home.yongli'))
            elif retur_re=='fail':
                case.Interface_is_tiaoshi = True
                case.Interface_tiaoshi_shifou = True
                if case.saveresult is True:
                    new_testre=TestcaseResult(case_id=case.id)
                    new_testre.result=str(result)
                    db.session.add(new_testre)
                db.session.commit()
                flash(u'用例测试失败')
                return redirect(next or url_for('home.yongli'))
            else:
                case.Interface_is_tiaoshi = True
                case.Interface_tiaoshi_shifou = True
                db.session.commit()
                flash(u'测试用例测试过程中出现异常！%s'%retur_re)
                return redirect(next or url_for('home.yongli'))
        except:
            db.session.rollback()
            flash(u'用例测试失败,失败原因：{},请检查测试用例'.format(retur_re))
            return redirect(next or url_for('home.yongli'))
class DuoyongliView(View):
    methods=['GET','POST']
    @login_required
    def dispatch_request(self):
        next=request.headers.get('Referer')
        starttime=datetime.datetime.now()
        star=time.time()
        day = time.strftime("%Y%m%d%H%M", time.localtime(time.time()))
        pad=os.getcwd()
        file_dir = pad+'\\app\\upload'
        file = os.path.join(file_dir, (day + '.log'))
        if os.path.exists(file) is False:
            os.system('touch %s' % file)
        filepath =os.path.join(file_dir,(day+'.html'))
        if os.path.exists(filepath) is False:
            os.system(r'touch %s' % filepath)
        if request.method=='POST':
            f_email=request.form.get('email')
            f_dingding=request.form.get('dingding')
            me=request.form.getlist('yongli')
            if len(me)<=1:
                flash(u'请选择一个以上的用例来执行')
                return redirect(next or url_for('yongli'))
            projecct_list=[]
            model_list=[]
            Interface_name_list=[]
            Interface_url_list=[]
            Interface_meth_list=[]
            Interface_pase_list=[]
            Interface_assert_list=[]
            Interface_headers_list=[]
            Interface_pid_list=[]
            Interface_yilai_list=[]
            Interface_save_list=[]
            id_list=[]
            for case in me:
                case_one=InterfaceTest.query.filter_by(id=case).first()
                id_list.append(case_one.id)
                projecct_list.append(case_one.projects)
                model_list.append(case_one.models)
                Interface_url_list.append(case_one.Interface_url)
                Interface_name_list.append(case_one.Interface_name)
                Interface_meth_list.append(case_one.Interface_meth)
                Interface_pase_list.append(case_one.Interface_pase)
                Interface_assert_list.append(case_one.Interface_assert)
                Interface_headers_list.append(case_one.Interface_headers)
                Interface_pid_list.append(case_one.pid)
                Interface_yilai_list.append(case_one.getattr_p)
                Interface_save_list.append(case_one.saveresult)
            if (len(set(projecct_list)))>1:
                flash('目前单次只能执行一个项目')
                return redirect(next or url_for('duoyongli'))
            try:
                apitest = ApiTestCase(inteface_url=Interface_url_list, inteface_meth=Interface_meth_list, inteface_parm=Interface_pase_list,
                                      inteface_assert=Interface_assert_list, file=file, headers=Interface_headers_list,pid=Interface_pid_list,
                                      yilaidata=Interface_yilai_list,saveresult=Interface_save_list,id_list=id_list)
                result_toal, result_pass, result_fail, relusts, bask_list,result_cashu,result_wei,result_except= apitest.testapi()
                endtime = datetime.datetime.now()
                end = time.time()
                createHtml(titles=u'接口测试报告', filepath=filepath, starttime=starttime, endtime=endtime,
                           passge=result_pass, fail=result_fail, id=id_list, name=projecct_list,
                           headers=Interface_headers_list, coneent=Interface_url_list, url=Interface_meth_list,
                           meth=Interface_pase_list, yuqi=Interface_assert_list, json=bask_list, relusts=relusts,
                           excepts=result_except, yuqis=result_cashu, weizhi=result_wei)
                hour = end - star
                user_id = User.query.filter_by(username=session.get('username')).first().id
                new_reust = TestResult(Test_user_id=user_id, test_num=result_toal, pass_num=result_pass,
                                       fail_num=result_fail, test_time=starttime, hour_time=hour,
                                       test_rep=(day + '.html'), test_log=(day + '.log'),Exception_num=result_except,can_num=result_cashu,
                                       wei_num=result_wei)
                db.session.add(new_reust)
                db.session.commit()
                if f_email == 'email':
                    email = EmailReport.query.filter_by(email_re_user_id=int(current_user.id),
                                                        default_set=True).first()
                    if email:
                        m = send_emails(sender=email.send_email, receivers=email.to_email,
                                        password=email.send_email_password,
                                        smtp=email.stmp_email, port=email.port, fujian1=file, fujian2=filepath,
                                        subject=u'%s用例执行测试报告' % day, url='http://127.0.0.1:5000/test_rep')
                        if m == False:
                            flash(u'发送邮件失败，请检查您默认的邮件设置是否正确')
                            return redirect(url_for('home.test_rep'))
                        flash(u'测试已经完成，并且给您默认设置发送了测试报告')
                        return redirect(url_for('home.test_rep'))
                    flash(u'无法完成，需要去您的个人设置去设置一个默认的邮件发送')
                    return redirect(url_for('home.yongli'))
                if f_dingding=='dingding':
                    send=send_ding(content="多用例测试已经完成，通过用例：%s，失败用例：%s，详情见测试报告"%(result_pass,result_fail))
                    if send is True:
                        flash(u'测试报告已经发送钉钉讨论群，测试报告已经生成！')
                        return redirect(url_for('home.yongli'))
                    flash(u'测试报告发送钉钉讨论群失败！请检查相关配置！')
                    return redirect(next or url_for('home.yongli'))
                flash(u'测试已经完成，测试报告已经生成')
                return redirect(url_for('home.test_rep'))
            except Exception as e:
                print(e)
                flash(u'测试失败，请检查您的测试用例单个执行是否出错')
                return redirect(next or url_for('home.yongli'))
        return redirect(url_for('home.yongli'))
class MakeonlyoneCase(View):#单个接口测试的代码，为了你的接口测试需要区分测试环境，没有测试环境的区别这里的代码可以注释掉
    methods = ['GET', 'POST']
    @login_required
    def dispatch_request(self):
        projec = (request.get_json())
        try:
            case_id=projec['caseid']
            url=projec['url']
            case=InterfaceTest.query.filter_by(id=int(case_id)).first()
            if case.pid != 'None' and case.pid !='' and case.pid is not None:
                tesyi=InterfaceTest.query.filter_by(id=int(case.pid)).first()
                if tesyi:
                    testres=TestcaseResult.query.filter_by(case_id=tesyi.id).first()
                    if testres is None:
                        case.Interface_is_tiaoshi = True
                        case.Interface_tiaoshi_shifou = True
                        db.session.commit()
                        return jsonify({'code': 131, 'msg': '找不到依赖的接口的测试结果！请查找依赖接口是否进行测试,获取测试是否通过,接口id是：%s'%(case.pid)})
                    huoquyilai=testres.result
                    canshu=case.getattr_p
                    try:
                        yilaidata=eval(huoquyilai)[canshu]
                    except Exception as e:
                        case.Interface_is_tiaoshi = True
                        case.Interface_tiaoshi_shifou = True
                        db.session.commit()
                        return jsonify({'code': 151, 'msg': '获取依赖数据失败，原因：%s' %e})
                    try:
                        pasrms = eval(case.Interface_pase)
                        pasrms.update({canshu: yilaidata})
                    except:
                        return jsonify({'code': 152, 'msg': '测试参数应该是字典格式！'})
                else:
                    pasrms=case.Interface_pase
            else:
                pasrms = case.Interface_pase
            new_headers=case.Interface_headers
            if  new_headers =='None':
                ne={'host':url}
            elif new_headers is None:
                ne = {'host': url}
            else:
                try:
                    ne=eval(new_headers)
                except:
                    return jsonify({'code': 110, 'msg': '测试的请求头应该是字典格式的！'})
            me = Api(url=case.Interface_url, fangshi=case.Interface_meth, params=pasrms,headers=ne)
            result = me.testapi()
            retur_re = assert_in(case.Interface_assert, result)
            try:
                if retur_re == 'pass':
                    case.Interface_is_tiaoshi = True
                    case.Interface_tiaoshi_shifou = False
                    if case.saveresult is True:
                        new_testre = TestcaseResult(case_id=case.id)
                        new_testre.result = str(result)
                        new_testre.testevir= url
                        new_testre.date = datetime.datetime.now()
                        db.session.add(new_testre)
                    db.session.commit()
                    return jsonify({'code':200,'msg':'测试用例调试通过！'})
                elif retur_re =='fail':
                    case.Interface_is_tiaoshi = True
                    case.Interface_tiaoshi_shifou = True
                    if case.saveresult is True:
                        new_testre = TestcaseResult(case_id=case.id)
                        new_testre.result = str(result)
                        new_testre.testevir = url
                        new_testre.date = datetime.datetime.now()
                        db.session.add(new_testre)
                    db.session.commit()
                    return jsonify({'code': 101, 'msg': '测试用例测试失败,原因：预期结果不一致，请检查用例！'})
                else:
                    case.Interface_is_tiaoshi = True
                    case.Interface_tiaoshi_shifou = True
                    if case.saveresult is True:
                        new_testre = TestcaseResult(case_id=case)
                        new_testre.result =str(result)
                        new_testre.testevir = url
                        new_testre.date = datetime.datetime.now()
                        db.session.add(new_testre)
                        db.session.commit()
                    return jsonify({'code': 102, 'msg': '测试返回异常，原因：%s,请检查用例！'%retur_re})
            except Exception as e:
                db.session.rollback()
                return jsonify({'code': 103, 'msg': u'用例测试失败,失败原因：{},请检查测试用例'.format(retur_re)})
        except Exception as e:
            print(e)
            return  jsonify({'code':100,'msg':'获取不到用例和测试环境的信息'})