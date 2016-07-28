sqn= [5,9,12,7,15,4,14,11,8,0,1,2,13,3,6,10];
sqn=sqn+11;
len=length(freq_inthop(:,1));
hopbaseddelay=zeros(6,len);
motebufferdelay=zeros(13,2);
slotsize=17 ;

for j=1:len
    for l=1:5
        if freq_inthop(j,l+1)~=0
            i=1;
            while sqn(i)~=freq_inthop(j,l)
                i=i+1;
            end
            if l==1
                hopbaseddelay(1,j)=mod(i-mod(asnfirst_inthop(j),16),16);
                motebufferdelay(hopaddr_inthop(j,l),1)=motebufferdelay(hopaddr_inthop(j,l),1)+hopbaseddelay(l+1,j);
                motebufferdelay(hopaddr_inthop(j,l),2)=motebufferdelay(hopaddr_inthop(j,l),2)+1;
            end
            k=1;
            while sqn(k)~=freq_inthop(j,l+1)
                k=k+1;
            end
            if hopaddr_inthop(j,l)<hopaddr_inthop(j,l+1)
                hopbaseddelay(l+1,j)=mod(k-(mod(hopaddr_inthop(j,l+1)-hopaddr_inthop(j,l)+i+(3-retx_inthop(j,l+1))*slotsize,16)),16);
                motebufferdelay(hopaddr_inthop(j,l+1),1)=motebufferdelay(hopaddr_inthop(j,l+1),1)+hopbaseddelay(l+1,j);
                motebufferdelay(hopaddr_inthop(j,l+1),2)=motebufferdelay(hopaddr_inthop(j,l+1),2)+1;
            else
                hopbaseddelay(l+1,j)=mod(k-(mod(slotsize+(hopaddr_inthop(j,l+1)-hopaddr_inthop(j,l))+i+(3-retx_inthop(j,l+1))*slotsize,16)),16);
                motebufferdelay(hopaddr_inthop(j,l+1),1)=motebufferdelay(hopaddr_inthop(j,l+1),1)+hopbaseddelay(l+1,j);
                motebufferdelay(hopaddr_inthop(j,l+1),2)=motebufferdelay(hopaddr_inthop(j,l+1),2)+1;
            end 
        end
    end

end

motebufferdelayavg=motebufferdelay(:,1)./motebufferdelay(:,2);
plot(motebufferdelayavg,'r+')
grid minor
