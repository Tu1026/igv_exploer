using  Statistics,StatsPlots, Plots, ForwardDiff, LinearAlgebra, Random,Printf, DataFrames
begin
	Random.seed!(317)   
	(m,n)=(5,2)
	A1=rand(2, 5)
	x = rand(2,1)
	xstart=[1000,-500]
	ν = .5*rand(5)
	δ=[norm(A1[:,i] -x) + ν[i] for i in 1:m]
end

struct State
	x::Vector
	f
	norm∇f
end

###computing gradient by creating function to find jacobian
begin
	function F(x)
		result=zeros(m,1)
		for i in 1:m
			result[i]=dot(x-A1[:,i],x-A1[:,i])-δ[i]^2
		end
		return result
	end
	
	function jac(x)
		result=zeros(m,n)
		for i in 1:m
			result[i,:]= 2 * (x-A1[:,i])
		end
		return result
	end
	
	sl2(x)=dot(F(x),F(x))
	grad_sl2(x)=2*jac(x)'*F(x)
	
end

begin
	# Gradient method with backtracking
	function grad_method_backtracking(f, g, x0; ϵ = 1e-4, μ = 0.5)
	    x = copy(x0)
	    fk = f(x); ∇fk = g(x)
	    k = 0
	    trace = [State(x, fk, norm(∇fk))]
	    while norm(∇fk) > ϵ 
	        α = 1.0
	        while ((fk - f(x-α*∇fk)) < μ*α*dot(∇fk,∇fk) )
	            α /=2
	        end
	        x = x - α*∇fk
	        fk = f(x); ∇fk = g(x)
	        k += 1
			# push!(trace, State(x, fk, norm(∇fk)))
	    end
        print(k)
	    return k
	end
end

function log(states::Vector{State})
	io = IOBuffer()
	write(io, "| k | f | ∇f | \n")
	write(io, "|---|---|---| \n")
	for (k, s) in enumerate(states)
		f = @sprintf("%10.2e", s.f)
		nrmf = @sprintf("%10.2e", s.norm∇f)
		write(io, "| $(k-1) | $f | $nrmf |\n")
	end
	Markdown.parse(seekstart(io))
end

collect(states::Vector{State}) = reduce(hcat, s.x for s in states)

k = grad_method_backtracking(sl2,grad_sl2, xstart, μ = 0.5);
print(k)
