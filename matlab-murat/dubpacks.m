
len=length(freq_nointhop(:,1));
slotsize=17;
motes=zeros(13,max(sqn_nointhop));
maxsqn=zeros(13,1);

for j=1:len
	motes(hopaddr_nointhop(j,1),sqn_nointhop(j))=motes(hopaddr_nointhop(j,1),sqn_nointhop(j))+1; 
    %motes(hopaddr_nointhop(j,1),sqn_nointhop(j))=1; 
    if maxsqn(hopaddr_nointhop(j,1))<sqn_nointhop(j)
        maxsqn(hopaddr_nointhop(j,1))=sqn_nointhop(j);
    end
end

duppacks=zeros(40,1);
for l=1:530
countmult=0;
count=0;
for j=(l)*10:(l+1)*10
    for i=1:13
        if motes(i,j)>1
            count=count+1;
            countmult=countmult+motes(i,j)-1;
        elseif motes(i,j)==1
            count=count+1;
        end    
    end
end
duppacks(l)=countmult/count;
end

plot(10:10:5300,duppacks);