from diagrams import Cluster, Diagram, Edge

#onprem
from diagrams.onprem.compute import Server as onprServer
from diagrams.onprem.database import Mysql as onprMysql
from diagrams.oci.network import Loadbalance as onprLB
from diagrams.onprem.client import Users
#oci
from diagrams.oci.connectivity import Fastconnect as onprFastconnect, Vpn as onprVpn
from diagrams.oci.edge import Dns as onprDns
from diagrams.oci.storage import Filestorage as nfs 
from diagrams.onprem.network import Nginx
from diagrams.oci.connectivity import Backbone

# aws
from diagrams.aws.database import RDS
from diagrams.aws.storage import S3
from diagrams.aws.compute import AutoScaling, EC2
from diagrams.aws.analytics import Glue
from diagrams.aws.network import CF,ELB,Route53, SiteToSiteVpn as s2s_vpn

from diagrams.aws.compute import Batch
from diagrams.aws.management import Cloudwatch as cw 

with Diagram("On-prem web application", show=False):
    dns = onprDns('Round-robin DNS ')
    users = Users('website/mobile users')
    nfs = nfs('Shared filesystem')

    with Cluster("Application Servers"):
        app_servers = [ onprServer("app_srv1"),
                        onprServer("app_srv2"),
                        onprServer("app_srv3")]
        Backbone = Backbone("Network")

    with Cluster("WebProxy Servers"):
        web_servers = [ Nginx("web_srv1"),
                        Nginx("web_srv2"),
                        Nginx("web_srv3")]

    with Cluster("Mysql active-active cluster"):
        db_master = onprMysql("userdb")
        db_master - [onprMysql("userdb")]

    users - dns >> web_servers
    web_servers >> Backbone
    Backbone >> app_servers
    app_servers >> db_master
    app_servers >> nfs

with Diagram("AWS web application", show=True):
    users = Users('website/mobile users')
    
        
    with Cluster("Ingress"):
        dns = Route53("Route53")
    
        with Cluster("Cloudfront CDN"):
            s3_content = S3('Shared content') 
            cf = CF('Cloudfront CDN')

    with Cluster('VPC'):
        with Cluster("WebProxy AutoScalingGroup (ASG)"):
            web_asg = AutoScaling('ASG')
            web_lb = ELB("NLB")

        with Cluster("Application servers AutoScalingGroup (ASG)"):
            app_asg = AutoScaling('ASG')
            app_lb = ELB("NLB")
    
        with Cluster("AWS Batch"):
            cwa = cw('CW Event')
            batch_s3 = S3('Batch data')
            batch = Batch('AWS Batch')
    
        with Cluster("DB Cluster"):
            db_master = RDS("master")
            db_master - [RDS("slave")]

    users >> dns
    users >> cf
    cf >> s3_content
    dns >> web_lb >> web_asg
    web_asg >> app_lb >> app_asg
    app_asg >> db_master
    app_asg >> batch_s3
    app_asg >> s3_content
    cwa >> batch << batch_s3
    batch_s3 >> db_master
