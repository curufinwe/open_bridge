require_relative './state_fast'

require 'wrong'
include Wrong

describe State do
  describe "#set_authoritative" do
    it "will set internal values" do
      s = State.new
      s.set_authoritative(%w{foo bar}, 3)
      internal= s.instance_eval{@authoritative}
      assert{internal["foo"]["bar"] == 3}
    end
  end

  describe "#set" do
    it "will set the values in diff" do
      s = State.new
      s.set(%w{foo bar}, 3)
      internal= s.instance_eval{@diff}
      assert{internal["foo"]["bar"] == 3}
    end

    it "will raise a exception if trying to set a hash as value" do
      s =State.new
      expect { s.set(%w{foo bar}, {}) }.to raise_error
    end
  end

  describe "#get" do
    it "will return the value stored under path from @proposed if contained in @proposed" do 
      s = State.new
      s.set_authoritative(%w{foo bar},3)
      s.set(%w{foo bar},4)
      s.prompote_diff_to_proposed
      assert{ s.get(%w{foo bar}) == 4}
    end

    it "will return the value stored in @authoritative part if not in @proposed" do
      s = State.new
      s.set_authoritative(%w{foo bar},3)
      assert{ s.get(%w{foo bar}) == 3}
    end

    it "will return nil for nonexisting paths" do
      s = State.new
      s.set_authoritative(%w{foo bar},3)
      assert{ s.get(%w{foo baz}) == nil}
    end
  end

  describe "#diff" do
    it "will return the current diff" do
      s =State.new
      s.set(%w{foo bar},3)
      s.set(%w{foo baz},4)
      assert{ s.diff == {"foo"=> {"bar" => 3, "baz"=> 4}} }
    end
  end

  describe "#apply_patch" do
    it "will apply the given diff to the authoritive state" do
      s = State.new
      s.set_authoritative(%w{bar},3)
      s.set_authoritative(%w{baz},5)
      diff = {"baz"=>4}
      s.apply_patch(diff)
      authoritative= s.instance_eval{@authoritative} 
      assert{authoritative  == {"bar" => 3, "baz" => 4} }
    end
  end

  describe "#reset_diff" do 
    it "resets diff to the empty diff" do
      s = State.new
      s.set(%w{foo bar},3)
      s.set(%w{foo baz},4)
      assert{ s.diff == {"foo"=> {"bar" => 3, "baz"=> 4}} }
      s.reset_diff
      assert{ s.diff == {} }
    end
  end

end
