#!/usr/bin/env python
# coding: utf-8

from bs4 import BeautifulSoup
from selenium import webdriver
from urllib import request
import os
import argparse

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--Company', type=str, default='Amazon', help='Company Name')
    parser.add_argument('--JobTitle', type=str, default='SDE', help='Job Title')
    parser.add_argument('--JobCount', type=int, default='200', help='Number of Jobs to Study')
    args = parser.parse_args()
    #args, unknown = parser.parse_known_args()
    args.DataDir = 'data'
    args.UrlDict = {
        'AmazonPref': 'https://www.amazon.jobs',
        'Amazon': 'https://www.amazon.jobs/en/search?offset={}&result_limit=10&sort=relevant&category[]={}&distanceType=Mi&radius=24km&loc_group_id=seattle-metro&latitude=&longitude=&loc_group_id=seattle-metro&loc_query=Greater%20Seattle%20Area%2C%20WA%2C%20United%20States&base_query=&city=&country=&region=&county=&query_options=&'
    }

    args.JobDict = {
        'AmazonDS': 'data-science',
        'AmazonRS': 'research-science',
        'AmazonML': 'machine-learning-science',
        'AmazonBI': 'business-intelligence',
        'AmazonSDE': 'software-development'
    }
    
    return args

class Top_Skill():
    
    def __init__(self, args):
        self.Company = args.Company
        self.JobTitle = args.JobTitle
        self.JobCount = args.JobCount
        self.DataDir = args.DataDir
        self.UrlDict = args.UrlDict
        self.JobDict = args.JobDict
        self.JobCategory = self.JobDict[self.Company + self.JobTitle]
        self.Links = None
        self.qualifications = None

        
    
    def get_job_links(self):
        '''
        Parameters
        ----------
        Company: string
        JobCategory: string
        JobCount: int
        '''
        
        job_count = (self.JobCount - 1) // 10 * 10 + 10
        offsets = range(0, job_count, 10)
        links = []
        for offset in offsets:
            url = self.UrlDict[self.Company].format(offset, self.JobCategory)
            soup = self.get_soup_from_url(url)
            for link in soup.find_all('a', {'class': 'job-link'}):
                links.append(self.UrlDict[self.Company + 'Pref'] + link.get('href'))
        
        return links
    
    def get_soup_from_url(self, url):
        '''
        Parameters
        ----------
        url: string
        '''
        
        driver = webdriver.Chrome()
        driver.get(url)
        html = driver.page_source
        soup = BeautifulSoup(html)
        driver.close()
        
        return soup
    
    def save_links(self):
        '''
        Parameters
        ----------
        DataDir: string
            Path to save data
            
        Company: string
        JobTitle: string
        Links: list
        '''

        if not os.path.exists(self.DataDir):
            os.makedirs(self.DataDir)
        if not self.Links:
            self.Links = self.get_job_links()
            
        link_dir = self.DataDir + '/' + self.Company + '_' + self.JobTitle + '_Links.txt'
            
        with open(link_dir, 'w') as f:
            for link in self.Links:
                f.write(link + '\n')
                
                
    def get_qualifications(self):
        '''
        Parameters
        ----------
        Company: string
        JobCategory: string
        Links: list
        ''' 
        
        qualifications = []
        if not self.Links:
            self.save_links()
            
        for link in self.Links:
            requirements, title = self.get_requirements_from_link(link)
            basic_qualification = requirements[1].p.get_text()
            preferred_qualification = BeautifulSoup(str(requirements[2].p).split('<br/><br/>')[0]).get_text()
            qualifications.append(self.Company + '\t' + self.JobCategory + '\t' + \
                                  title + '\t' + basic_qualification + '\t' + \
                                  preferred_qualification + '\t' + link)
        
        return qualifications
    
    def get_requirements_from_link(self, link):
        '''
        Parameters
        ----------
        Company: string
        JobCategory: string
        link: string
        '''
        
        response = request.urlopen(link)
        page_source = response.read().decode('utf-8')
        soup = BeautifulSoup(page_source)
        requirements = soup.find_all('div', {'class': 'section'})
        title = soup.find_all('h1', {'class': 'title'})[0].get_text()
        
        return requirements, title
        
    
    def save_qualifications(self):
        '''
        Parameters
        ----------
        DataDir: string
            Path to save data
            
        Company: string
        JobTitle: string
        qualifications: list
        '''

        if not self.qualifications:
            self.qualifications = self.get_qualifications()
            
        data_file_dir = self.DataDir + '/' + self.Company + '_' + self.JobTitle + '_Qualifications.txt'
            
        with open(data_file_dir, 'w') as f:
            f.write('Company\t' + 'Category\t' + 'Job_Title\t' + \
                    'Basic_Qualifications\t' + \
                    'Preferred_Qualifications\t' + 'Job_URL\n')
            
            for row in self.qualifications:
                f.write(row + '\n')
        
        

if __name__ == '__main__':
    args = get_args()
    data = Top_Skill(args)
    data.save_qualifications()

