
len=length(freq_sharedindinthop(:,1));
slotsize=17;
motes=zeros(13,max(sqn_sharedindinthop));
maxsqn=zeros(13,1);
deadline=2000;%ms
timeslot=15;%ms
ASNdeadline=ceil(deadline/timeslot);
x=5;
for j=1:len
	%motes(hopaddr_sharedindinthop(j,1),sqn_sharedindinthop(j))=motes(hopaddr_sharedindinthop(j,1),sqn_sharedindinthop(j))+1; 
    
    %if (asnlast_sharedindinthop(j)-asnfirst_sharedindinthop(j))<ASNdeadline
    	motes(hopaddr_sharedindinthop(j,1),sqn_sharedindinthop(j))=1;

   % end
        maxsqn=max(motessqnsharedindinthop');
end
motesrel=sum(permute(motes,[2 1]))./maxsqn;
dummy=(x+1)*ones(1,10);
%plot(1:13,motesrel(1:13));
for j=1:10
    scatterx(j+x*10)=dummy(j);
    scattery(j+x*10)=motesrel(1+j);
    scatterr(j+x*10)=maxsqn(1+j);
end