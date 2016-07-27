
len=length(freq_sharednointhop(:,1));
slotsize=17;
motes=zeros(13,max(sqn_sharednointhop));
maxsqn=zeros(13,1);
deadline=2000;%ms
timeslot=15;%ms
ASNdeadline=ceil(deadline/timeslot);

for j=1:len
	%motes(hopaddr_sharednointhop(j,1),sqn_sharednointhop(j))=motes(hopaddr_sharednointhop(j,1),sqn_sharednointhop(j))+1; 
    
    if (asnlast_sharednointhop(j)-asnfirst_sharednointhop(j))<ASNdeadline
    	motes(hopaddr_sharednointhop(j,1),sqn_sharednointhop(j))=1;
        if maxsqn(hopaddr_sharednointhop(j,1))<sqn_sharednointhop(j)
            maxsqn(hopaddr_sharednointhop(j,1))=sqn_sharednointhop(j);
        end
    end

end
motesrel=sum(motes')./maxsqn';

plot(1:13,motesrel(1:13));
hold 

len=length(freq_sharedinthop(:,1));
motes=zeros(13,max(sqn_sharedinthop));
maxsqn=zeros(13,1);

for j=1:len
	%motes(hopaddr_sharedinthop(j,1),sqn_sharedinthop(j))=motes(hopaddr_sharedinthop(j,1),sqn_sharedinthop(j))+1; 
    
    if (asnlast_sharedinthop(j)-asnfirst_sharedinthop(j))<ASNdeadline
    	motes(hopaddr_sharedinthop(j,1),sqn_sharedinthop(j))=1;
        if maxsqn(hopaddr_sharedinthop(j,1))<sqn_sharedinthop(j)
            maxsqn(hopaddr_sharedinthop(j,1))=sqn_sharedinthop(j);
        end
    end

end
motesrel=sum(motes')./maxsqn';


plot(1:13,motesrel(1:13));
legend('no int','int')

