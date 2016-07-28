
sqn= [5,9,12,7,15,4,14,11,8,0,1,2,13,3,6,10];
sqn=sqn+11;
len=length(freq_dumbinthop(:,1));
packetsuc=zeros(16,13,13); %freq,src,dest
packetcol=zeros(13,13);
packetcount=zeros(16,13,13);
for j=1:len
    for l=1:5
        if freq_dumbinthop(j,l)~=0
        i=1;
        while sqn(i)~=freq_dumbinthop(j,l)
        	i=i+1;
        end
        if freq_dumbinthop(j,l+1)~=0
            if retx_dumbinthop(j,l)==3
                packetsuc(freq_dumbinthop(j,l)-10,hopaddr_dumbinthop(j,l),hopaddr_dumbinthop(j,l+1))=packetsuc(freq_dumbinthop(j,l)-10,hopaddr_dumbinthop(j,l),hopaddr_dumbinthop(j,l+1))+1;
                packetcount(freq_dumbinthop(j,l)-10,hopaddr_dumbinthop(j,l),hopaddr_dumbinthop(j,l+1))=packetcount(freq_dumbinthop(j,l)-10,hopaddr_dumbinthop(j,l),hopaddr_dumbinthop(j,l+1))+1;
            elseif retx_dumbinthop(j,l)==2
                packetsuc(freq_dumbinthop(j,l)-10,hopaddr_dumbinthop(j,l),hopaddr_dumbinthop(j,l+1))=packetsuc(freq_dumbinthop(j,l)-10,hopaddr_dumbinthop(j,l),hopaddr_dumbinthop(j,l+1))+1;
                packetcount(freq_dumbinthop(j,l)-10,hopaddr_dumbinthop(j,l),hopaddr_dumbinthop(j,l+1))=packetcount(freq_dumbinthop(j,l)-10,hopaddr_dumbinthop(j,l),hopaddr_dumbinthop(j,l+1))+1;
                packetcol(hopaddr_dumbinthop(j,l),hopaddr_dumbinthop(j,l+1))=packetcol(hopaddr_dumbinthop(j,l),hopaddr_dumbinthop(j,l+1))+1;
            elseif retx_dumbinthop(j,l)==1
                packetsuc(freq_dumbinthop(j,l)-10,hopaddr_dumbinthop(j,l),hopaddr_dumbinthop(j,l+1))=packetsuc(freq_dumbinthop(j,l)-10,hopaddr_dumbinthop(j,l),hopaddr_dumbinthop(j,l+1))+1;
                packetcount(freq_dumbinthop(j,l)-10,hopaddr_dumbinthop(j,l),hopaddr_dumbinthop(j,l+1))=packetcount(freq_dumbinthop(j,l)-10,hopaddr_dumbinthop(j,l),hopaddr_dumbinthop(j,l+1))+1;
                packetcol(hopaddr_dumbinthop(j,l),hopaddr_dumbinthop(j,l+1))=packetcol(hopaddr_dumbinthop(j,l),hopaddr_dumbinthop(j,l+1))+2;  
            end             
        else
            if retx_dumbinthop(j,l)==3
                packetsuc(freq_dumbinthop(j,l)-10,hopaddr_dumbinthop(j,l),1)=packetsuc(freq_dumbinthop(j,l)-10,hopaddr_dumbinthop(j,l),1)+1;
                packetcount(freq_dumbinthop(j,l)-10,hopaddr_dumbinthop(j,l),1)=packetcount(freq_dumbinthop(j,l)-10,hopaddr_dumbinthop(j,l),1)+1;
            elseif retx_dumbinthop(j,l)==2
                packetsuc(freq_dumbinthop(j,l)-10,hopaddr_dumbinthop(j,l),1)=packetsuc(freq_dumbinthop(j,l)-10,hopaddr_dumbinthop(j,l),1)+1;
                packetcount(freq_dumbinthop(j,l)-10,hopaddr_dumbinthop(j,l),1)=packetcount(freq_dumbinthop(j,l)-10,hopaddr_dumbinthop(j,l),1)+1;
                packetcol(hopaddr_dumbinthop(j,l),1)=packetcol(hopaddr_dumbinthop(j,l),1)+1;
            elseif retx_dumbinthop(j,l)==1
                packetsuc(freq_dumbinthop(j,l)-10,hopaddr_dumbinthop(j,l),1)= packetsuc(freq_dumbinthop(j,l)-10,hopaddr_dumbinthop(j,l),1)+1;
                packetcount(freq_dumbinthop(j,l)-10,hopaddr_dumbinthop(j,l),1)=packetcount(freq_dumbinthop(j,l)-10,hopaddr_dumbinthop(j,l),1)+1;
                packetcol(hopaddr_dumbinthop(j,l),1)=packetcol(hopaddr_dumbinthop(j,l),1)+2; 
            end               
        end
            

        end
    end
end

%allpathsplot
%packetrel=packetsuc./packetcount;
%freqpath=zeros(16,14*13);
%freqpath2=zeros(13*13,1);
%for i=1:13
%    for j=1:13
%        if sum(packetrel(:,i,j)>0)
%            freqpath(:,i+j*13)=packetrel(:,i,j);
%            freqpath2(i+j*13)=1;
%        end
%    end
%end
%bar3(freqpath(:,14:26));


%distribute collisions
for i=1:16
    for j=1:13
        for k=1:13
            packetcount(i,j,k)=packetcount(i,j,k)+packetcol(j,k)/16;          
        end
    end
end





%bestdestinationplot
maindest=zeros(16,13);
maxcheck=zeros(16,13);
lastdest=zeros(1,13);
for i=1:13
    for j=1:13
       if sum(maxcheck(:,i))<sum(packetcount(:,i,j))
            maxcheck(:,i)=sum(packetcount(:,i,j));
            maindest(:,i)=packetsuc(:,i,j)./packetcount(:,i,j);
            lastdest(i)=j;
        end
    end
end







fig=figure('Units','inches',...
'Position',[5 5 5 3],...
'PaperPositionMode','auto');

b=bar3(1-maindest(:,2:12));
for k = 1:length(b)
    zdata = b(k).ZData;
    b(k).CData = zdata;
    b(k).FaceColor = 'interp';
end
colormap(flipud(hot))
%clear xlabel

axis([0 12 0 20])

set(gca,...
'XTick',1:11, 'XTickLabel',2:12,...
'YTick',1:16, 'YTickLabel',11:26,...
'Units','normalized',...
'FontUnits','points',...
'FontWeight','normal',...
'FontSize',10,...
'FontName','Helvetica')

ylabel({'Channels'},...
'FontUnits','points',...
'interpreter','latex',...
'FontSize',10,...
'FontName','Helvetica')

xlabel('Mote Address',...
'FontUnits','points',...
'interpreter','latex',...
'FontSize',10,...
'FontName','Helvetica')

view([270 90])
c=colorbar('east');
ax = gca;
axpos = ax.Position;
cpos = c.Position;

cpos(3) = 0.5*cpos(3);
c.Position = cpos;
ax.Position = axpos;


if 0
print(fig,'heatmapmedsharelowint','-depsc2')

f = 'heatmapmedsharelowint.eps';
eps = fileread(f);
fd = fopen(f, 'wt');
fwrite(fd, eps);
fclose(fd);
system(['epstopdf ' f]);
end

%print(fig,'heatmapmedsharedhighint','-dpdf','-r0')

%averagefreqplot
%succ=sum(sum(permute(packetsuc,[2 3 1])));
%count=sum(sum(permute(packetcount,[2 3 1])));

%count2=succ./count;
%for i=1:16
%   count3(i)=count2(1,1,i);
%end
%plot(count3);

        

