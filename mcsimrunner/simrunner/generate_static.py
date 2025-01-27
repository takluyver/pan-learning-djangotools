#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Generates static html browser pages for simrunner data output.
Uses django templates to generate the html.
'''
from django.template import Context
from os.path import basename, join, splitext
from django.template.loader import get_template
from django.template.loader import render_to_string

class McStaticDataBrowserGenerator():
    ''' implements functionality to generate static html site for data browsing '''   

    __base_c_dict = None
    def set_base_context(self, dict):
        ''' sets the dict that is passed to every context '''
        self.__base_c_dict = dict
    def get_context(self, dict):
        ''' combile "local" context with base context set at the beginning '''
        d = self.__base_c_dict.copy()
        d.update(dict)
        return Context(d) 

    def generate_browsepage(self, base_context, plot_files, dat_files):
        ''' plot_files AND dat_files must be of the correct path relative to data_folder 
            note: having dat_files be relative paths reduces assumptions and increases flexibility
        '''
        data_folder = base_context.get("data_folder")
        # get data for browse.html
        html_png_dat = []
        for i in range(len(plot_files)):
            png = plot_files[i]
            dat = dat_files[i]
            html = splitext(plot_files[i])[0] + '_w.html'
            html_png_dat.append([html, png, dat])

        # create twin data for log
        html_png_dat_log = []
        for i in range(len(plot_files)):
            png = splitext(plot_files[i])[0] + '_log' + splitext(plot_files[i])[1]
            dat = dat_files[i]
            html = splitext(plot_files[i])[0] + '_log_w.html'
            html_png_dat_log.append([html, png, dat])

        # 1) write <monitor>.html:

        # prepare strings
        png_base = map(lambda p: basename(p), plot_files)
        dat_base = map(lambda d: basename(d), dat_files)
        html_paths = map(lambda p: join(data_folder, '%s%s' % (splitext(p)[0], '_w.html')), plot_files)
        html_paths_log = map(lambda p: join(data_folder, '%s%s' % (splitext(p)[0], '_log_w.html')), plot_files)

        # get template for <monitor>.html
        templ='static_monitor.html'

        # write <monitor>.html and <monitor>_log.html for each png/dat file
        for i in range(len(plot_files)):
            png_dat = [png_base[i], dat_base[i]]

            c = {'png_dat': png_dat, 'twin_html': basename(html_paths_log[i]), 'lin_or_log': 'log'}
            c.update(base_context)
            write_html(html_paths[i], render_to_string(templ,c))

            # log versions of monitor files
            png_dat_log = [splitext(png_base[i])[0] + '_log.html', dat_base[i]]

            c = {'png_dat': png_dat_log, 'twin_html': basename(html_paths[i]), 'lin_or_log': 'lin'}
            c.update(base_context)
            write_html(html_paths_log[i], render_to_string(templ,c))

        # 2) write browse.html

        templ='static_browse.html'
        c = {'html_png_dat': html_png_dat, 'twin_html': 'browse_log.html', 'lin_or_log': 'log'}
        c.update(base_context)
        write_html(join(data_folder, 'browse.html'), render_to_string(templ,c))

        c = {'html_png_dat': html_png_dat_log, 'twin_html': 'browse.html', 'lin_or_log': 'lin'}
        c.update(base_context)
        write_html(join(data_folder, 'browse_log.html'), render_to_string(templ,c))

    def generate_browsepage_sweep(self, base_context, plot_files, dat_files, scanpoints):
        ''' as above, but handles the simulation scan case '''
        
        data_folder = base_context.get("data_folder")
        # prepare strings
        plt_base = map(lambda p: basename(p), plot_files)
        dat_base = map(lambda d: basename(d), dat_files)
        html_paths = map(lambda p: join(data_folder, '%s%s' % (splitext(p)[0], '_w.html')), plot_files)
        html_paths_log = map(lambda p: join(data_folder, '%s%s' % (splitext(p)[0], '_log_w.html')), plot_files)

        # 1) write <monitor>.html:

        # write <monitor>.html for each plt/dat file
        templ='static_monitor.html'
        for j in range(scanpoints):
            for i in range(len(plot_files)):
                if i == 0:
                    continue
                plt = plt_base[i].replace('/0/', '/%s/' % str(j))
                dat = dat_base[i].replace('/0/', '/%s/' % str(j))

                plt_dat = [plt, dat]
                c = {'png_dat': plt_dat, 'twin_html': basename(html_paths_log[i]).replace('/0/', '/%s/' % str(j)), 'lin_or_log': 'log'}
                c.update(base_context)
                write_html(html_paths[i].replace('/0/', '/%s/' % str(j)), render_to_string(templ,c))

                # write twin - log scale
                plt_dat = [splitext(plt)[0] + '_log' + splitext(plt)[1], dat]
                c = {'png_dat': plt_dat, 'twin_html': basename(html_paths[i].replace('/0/', '/%s/' % str(j))), 'lin_or_log': 'lin'}
                c.update(base_context)
                write_html(html_paths_log[i].replace('/0/', '/%s/' % str(j)), render_to_string(templ,c))

        # special case: mccode.dat : sweep overview
        plt_dat = [plt_base[0], dat_base[0]]
        c = {'png_dat': plt_dat}
        c.update(base_context)
        write_html(html_paths[0], render_to_string(templ,c))

        # log twin for that..
        plt_dat = [splitext(plt_base[0])[0] + '_log' + splitext(plt_base[0])[1], dat_base[0]]
        c = {'png_dat': plt_dat}
        c.update(base_context)
        write_html(splitext(html_paths[0])[0] + '_log.html', render_to_string(templ,c))

        # 2 write <monitor>_ss.html

        # get data for each monitor_ss.html and write it immediately
        templ='static_monitor_sweep.html'
        for i in range(len(plot_files)):
            if i == 0:
                continue

            # lin versions
            html_plt_dat = []
            monitor_name = splitext(basename(plot_files[i]))[0]
            for j in range(scanpoints):
                plt = plot_files[i].replace('/0/', '/%s/' % str(j))
                dat = dat_files[i].replace('/0/', '/%s/' % str(j))
                html = splitext(plot_files[i])[0] + '_w.html'
                html = html.replace('/0/', '/%s/' % str(j))
                html_plt_dat.append([html, plt, dat])

            # log
            html_plt_dat_log = []
            monitor_name = splitext(basename(plot_files[i]))[0]
            for j in range(scanpoints):
                plt = plot_files[i].replace('/0/', '/%s/' % str(j)) # insert correct sweep index
                plt = splitext(plt)[0] + '_log' + splitext(plt)[1] # insert "_log" into the file name
                dat = dat_files[i].replace('/0/', '/%s/' % str(j)) # data file is the same
                html = splitext(plot_files[i])[0] + '_log_w.html'
                html = html.replace('/0/', '/%s/' % str(j))
                html_plt_dat_log.append([html, plt, dat])
            
            c = {'monitor_name': monitor_name, 'html_png_dat': html_plt_dat, 'twin_html': '%s_sweep_log.html' % monitor_name, 'lin_or_log': 'log'}
            c.update(base_context)
            write_html(join(data_folder, '%s_sweep.html' % monitor_name), render_to_string(templ,c))

            c = {'monitor_name': monitor_name, 'html_png_dat': html_plt_dat_log, 'twin_html': '%s_sweep.html' % monitor_name, 'lin_or_log': 'lin'}
            c.update(base_context)
            write_html(join(data_folder, '%s_sweep_log.html' % monitor_name), render_to_string(templ,c))

        # 3) write browse.html

        # get data for browse_ss.html
        # the list html_name contains list of monitors (monitor.0 is html filepath,  monitor.1 is monitor displayname)
        sim_html = join(data_folder, 'mcstas', 'mccode.html')
        sim_html_log = join(data_folder, 'mcstas', 'mccode_log.html')
        sim_png = plot_files[0]
        sim_png_log = splitext(plot_files[0])[0] + '_log' + splitext(plot_files[0])[1]

        html_name = []
        for i in range(len(plot_files)):
            if i == 0:
                continue # avoid index 0 at all cost for sweeps!

            monitor_name = splitext(basename(plot_files[i]))[0]
            html_filepath = join(data_folder, '%s_sweep.html' % monitor_name)
            html_name.append([html_filepath, monitor_name])

        html_name_log = []
        for i in range(len(plot_files)):
            if i == 0:
                continue # avoid index 0 at all cost for sweeps!

            monitor_name = splitext(basename(plot_files[i]))[0]
            html_filepath = join(data_folder, '%s_sweep_log.html' % monitor_name)
            html_name_log.append([html_filepath, monitor_name])

        # write browse.html
        templ='static_browse_sweep.html'
        c = {'sim_html': sim_html, 'sim_png': sim_png, 'html_name': html_name, 'twin_html': 'browse_log.html', 'lin_or_log': 'log'}
        c.update(base_context)
        write_html(join(data_folder, 'browse.html'), render_to_string(templ,c))

        # browse_log.html
        t = get_template('static_browse_sweep.html')
        c = {'sim_html': sim_html_log, 'sim_png': sim_png_log, 'html_name': html_name_log, 'twin_html': 'browse.html', 'lin_or_log': 'lin'}
        c.update(base_context)
        write_html(join(data_folder, 'browse_log.html'), render_to_string(templ,c))


def write_html(filepath, text):
    ''' writes file <filepath> with content <text> to disk '''
    f = open(filepath, 'w')
    f.write(text)
    f.close()
